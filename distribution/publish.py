"""GitHub Actions publication of previously signed, byte-verified packages."""
from pathlib import Path
import base64,hashlib,io,json,os,time,urllib.error,urllib.parse,urllib.request,xml.etree.ElementTree as ET,zipfile,zlib

ROOT=Path(__file__).resolve().parent
REPO='contentriumkorea/local-studio-plugins'

def sha(data):return hashlib.sha256(data).hexdigest()

def api(path,data=None,method=None):
    url=path if path.startswith('https://') else 'https://api.github.com/repos/'+REPO+path
    if urllib.parse.urlparse(url).hostname not in ('api.github.com','uploads.github.com'):
        raise ValueError('Unexpected GitHub API host')
    headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','User-Agent':'LocalStudio-release','X-GitHub-Api-Version':'2022-11-28'}
    if isinstance(data,dict):data=json.dumps(data).encode();headers['Content-Type']='application/json'
    elif data is not None:headers['Content-Type']='application/octet-stream'
    request=urllib.request.Request(url,data=data,headers=headers,method=method)
    with urllib.request.urlopen(request,timeout=180) as response:return json.load(response)

def download(url):
    if not url.startswith('https://github.com/'+REPO+'/releases/download/'):
        raise ValueError('Unexpected asset URL')
    with urllib.request.urlopen(url,timeout=180) as response:return response.read()

def manifest(name):
    envelope=json.loads((ROOT.parent/'updates'/name).read_text())
    payload=base64.b64decode(envelope['payload']);signature=base64.b64decode(envelope['signature'])
    key=ET.fromstring((ROOT/'public-key.xml').read_text())
    modulus=int.from_bytes(base64.b64decode(key.findtext('Modulus')),'big')
    exponent=int.from_bytes(base64.b64decode(key.findtext('Exponent')),'big')
    size=(modulus.bit_length()+7)//8
    assert len(signature)==size
    digest_info=bytes.fromhex('3031300d060960864801650304020105000420')+hashlib.sha256(payload).digest()
    expected=b'\x00\x01'+b'\xff'*(size-len(digest_info)-3)+b'\x00'+digest_info
    assert pow(int.from_bytes(signature,'big'),exponent,modulus).to_bytes(size,'big')==expected,'Release signature mismatch'
    return json.loads(payload)

def ensure_release(tag,title,body):
    try:return api('/releases/tags/'+tag)
    except urllib.error.HTTPError as error:
        if error.code!=404:raise
    return api('/releases',{'tag_name':tag,'target_commitish':os.environ['GITHUB_SHA'],'name':title,'body':body,'draft':False,'prerelease':False,'make_latest':'false'})

def upload(release,name,data):
    assets=api('/releases/'+str(release['id'])+'/assets')
    old=next((item for item in assets if item['name']==name),None)
    digest='sha256:'+sha(data)
    if old:
        assert old['size']==len(data) and old.get('digest')==digest,'Existing release asset differs; refusing replacement'
        print('Already verified:',name,digest,flush=True);return
    url=release['upload_url'].split('{')[0]+'?'+urllib.parse.urlencode({'name':name})
    item=api(url,data,'POST')
    assert item['size']==len(data) and item.get('digest')==digest,'Uploaded asset digest mismatch'
    print('Uploaded and verified:',name,digest,flush=True)

def verify_package(data,info):
    assert len(data)==info['size'] and sha(data)==info['sha256'],'Package hash/size mismatch'
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        metadata=json.loads(package.read('product.json'))
        assert metadata['id']==info['product'] and metadata['version']==info['version']
        assert package.testzip() is None

def main():
    metadata=json.loads((ROOT/'package-input.json').read_text())
    recipe_bytes=(ROOT/'pin-package.zlib').read_bytes()
    assert sha(recipe_bytes)==metadata['recipe_sha256']
    recipe=json.loads(zlib.decompress(recipe_bytes))
    skin=manifest('skin-blur.json');pin=manifest('pin.json');legacy=manifest('glam.json')
    version=pin['version']
    source=download(recipe['source_url']);assert sha(source)==recipe['source_sha256']
    verify_package(source,skin)
    target=bytearray()
    for segment in recipe['segments']:
        target.extend(base64.b64decode(segment['literal']) if 'literal' in segment else source[segment['offset']:segment['offset']+segment['length']])
    target=bytes(target);assert sha(target)==recipe['target_sha256']
    verify_package(target,pin);verify_package(source,legacy)
    with zipfile.ZipFile(io.BytesIO(target)) as payload:
        updater=payload.read('PinUpdater.exe')
    assert sha(updater)==metadata['pin_updater_sha256']
    files={'PinLocalSetup.exe':updater,'PinLocal-update.json':(ROOT.parent/'updates/pin.json').read_bytes(),'PinLocal-'+version+'-Windows.zip':target}
    outer=io.BytesIO()
    with zipfile.ZipFile(outer,'w',zipfile.ZIP_STORED) as setup:
        for entry in metadata['outer_entries']:
            info=zipfile.ZipInfo(entry['filename'],tuple(entry['date_time']))
            for field in ('create_system','create_version','extract_version','internal_attr','external_attr'):setattr(info,field,entry[field])
            setup.writestr(info,files[entry['filename']])
    setup_bytes=outer.getvalue();assert sha(setup_bytes)==metadata['pin_setup_sha256'],'Setup reconstruction differs'
    release=ensure_release('pin-v'+version,'Pin Local '+version,
        '## 설치\nPinLocal-'+version+'-Setup.zip을 풀고 PinLocalSetup.exe를 실행하세요. Adobe 앱 종료 후 설치와 Windows 관리자 승인을 진행합니다.\n\n'+pin['notes']+
        '\n## 가림 뒤 이어 추적\n중단 지점 보기 → 얼굴이 다시 보이는 프레임으로 이동 → 원래 핀과 같은 위치를 같은 순서로 재지정 → 이어 추적 → 적용. 누락 구간은 수동 연결로 표시하며 재생 확인이 필요합니다. 자동으로 전부 추적한 결과와 구분됩니다.\n\nWindows x64 · CPU · SDR 8비트. 일반 설치는 Setup.zip 하나를 받으세요.')
    upload(release,'PinLocal-'+version+'-Windows.zip',target)
    upload(release,'PinLocal-update.json',files['PinLocal-update.json'])
    upload(release,'PinLocal-'+version+'-Setup.zip',setup_bytes)
    migration=ensure_release('glam-v0.2.1','Skin Blur 0.2.1 · 기존 업데이트 호환',
        '이 릴리스는 기존 Glam Local 0.2.0 업데이트 앱이 Skin Blur 0.2.1로 전환할 때 사용하는 호환 파일입니다.\n\n'
        '[새 설치는 Skin Blur 릴리스](https://github.com/'+REPO+'/releases/tag/skin-blur-v0.2.1)를 이용하세요. 기존 앱이 파일명을 검증하므로 이 호환 파일만 이전 이름을 유지합니다. 실제 설치되는 제품은 Skin Blur입니다.')
    upload(migration,'GlamLocal-0.2.1-Windows.zip',source)
    upload(migration,'GlamLocal-update.json',(ROOT.parent/'updates/glam.json').read_bytes())
    # Read back each published URL and verify the independently signed hash.
    for info in (pin,skin,legacy):
        data=download(info['url']);verify_package(data,info)
        print('PUBLIC_DOWNLOAD_VERIFIED',info['product'],info['version'],info['sha256'],flush=True)
    result={'status':'complete','pin':pin['url'],'skin_blur':skin['url'],'legacy':legacy['url'],'signed_feeds_verified':3,'public_downloads_verified':3,'private_key_uploaded':False}
    path='distribution/verification.json'
    try:old=api('/contents/'+path)
    except urllib.error.HTTPError as error:
        if error.code!=404:raise
        old=None
    body={'message':'Verify published Pin and Skin Blur signed downloads','content':base64.b64encode((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()).decode(),'branch':'main'}
    if old:body['sha']=old['sha']
    api('/contents/'+path,body,'PUT')
    print('PUBLICATION_COMPLETE',flush=True)

if __name__=='__main__':main()

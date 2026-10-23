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
    if recipe['source_url']==skin['url']:verify_package(source,skin)
    target=bytearray()
    for segment in recipe['segments']:
        target.extend(base64.b64decode(segment['literal']) if 'literal' in segment else source[segment['offset']:segment['offset']+segment['length']])
    target=bytes(target);assert sha(target)==recipe['target_sha256']
    verify_package(target,pin)
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
        '## 설치\n[경량 설치프로그램](https://github.com/'+REPO+'/releases/download/pin-v'+version+'/PinLocalSetup.exe)을 실행하면 최신 정식 버전을 내려받습니다. Adobe 앱 작업을 저장하고 종료한 뒤 설치와 Windows 관리자 승인을 진행하세요. 오프라인 설치는 Setup.zip을 사용하세요.\n\n'+pin['notes']+
        '\n## 사용\n원본 컷 불러오기 → 대상 글자·이미지 선택 또는 피사체 고정 → 핀 지정 → 추적 시작 → 결과 확인 → 적용. 가려져도 남은 프레임에서 같은 피사체를 다시 찾습니다. 가림 사이의 추정 구간과 미해결 구간은 별도로 표시합니다.\n\n## 검증 범위\n로컬 엔진과 설치 패키지를 검증했습니다. Premiere 실사용 검증은 사용자가 진행합니다. Windows x64 · Premiere Pro 26 · SDR 8비트.')
    upload(release,'PinLocal-'+version+'-Windows.zip',target)
    upload(release,'PinLocal-update.json',files['PinLocal-update.json'])
    upload(release,'PinLocal-'+version+'-Setup.zip',setup_bytes)
    upload(release,'PinLocalSetup.exe',updater)
    if legacy['version']=='0.2.1':
        migration=ensure_release('glam-v0.2.1','Skin Blur 0.2.1 · 기존 업데이트 호환',
            '이 릴리스는 기존 Glam Local 0.2.0 업데이트 앱이 Skin Blur 0.2.1로 전환할 때 사용하는 호환 파일입니다.\n\n'
            '[새 설치는 Skin Blur 릴리스](https://github.com/'+REPO+'/releases/tag/skin-blur-v0.2.1)를 이용하세요. 기존 앱이 파일명을 검증하므로 이 호환 파일만 이전 이름을 유지합니다. 실제 설치되는 제품은 Skin Blur입니다.')
        upload(migration,'GlamLocal-0.2.1-Windows.zip',source)
        upload(migration,'GlamLocal-update.json',(ROOT.parent/'updates/glam.json').read_bytes())
    # Read back each published URL and verify the independently signed hash.
    for info in (pin,skin,legacy):
        data=download(info['url']);verify_package(data,info)
        print('PUBLIC_DOWNLOAD_VERIFIED',info['product'],info['version'],info['sha256'],flush=True)
    installer_url='https://github.com/'+REPO+'/releases/download/pin-v'+version+'/PinLocalSetup.exe'
    assert sha(download(installer_url))==sha(updater),'Public installer download differs'
    result={'status':'complete','pin_version':version,'pin':pin['url'],'installer':installer_url,'installer_sha256':sha(updater),'skin_blur':skin['url'],'legacy':legacy['url'],'signed_feeds_verified':3,'public_downloads_verified':4,'private_key_uploaded':False}
    path='distribution/verification.json'
    try:old=api('/contents/'+path)
    except urllib.error.HTTPError as error:
        if error.code!=404:raise
        old=None
    body={'message':'Verify published Pin and Skin Blur signed downloads','content':base64.b64encode((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()).decode(),'branch':'main'}
    if old:body['sha']=old['sha']
    api('/contents/'+path,body,'PUT')
    print('PUBLICATION_COMPLETE',flush=True)

if __name__=='__main__':
    active=json.loads((ROOT/'package-input.json').read_text())
    if active.get('product')=='glam':
        from publish_skin import publish_skin
        publish_skin(active)
    else:main()

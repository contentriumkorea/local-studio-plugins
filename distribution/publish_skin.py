"""Publish the signed skin update; leave the Pin release and feed untouched."""
import base64,io,json,urllib.error,zipfile,zlib
from publish import ROOT,REPO,sha,api,download,manifest,verify_package,ensure_release,upload


def publish_skin(metadata):
    recipe_bytes=(ROOT/'skin-package.zlib').read_bytes()
    assert sha(recipe_bytes)==metadata['recipe_sha256']
    recipe=json.loads(zlib.decompress(recipe_bytes))
    source=download(recipe['source_url']);assert sha(source)==recipe['source_sha256']
    target=b''.join(base64.b64decode(s['literal']) if 'literal' in s else source[s['offset']:s['offset']+s['length']] for s in recipe['segments'])
    assert sha(target)==recipe['target_sha256']
    skin=manifest('skin-blur.json');legacy=manifest('glam.json');version=skin['version']
    verify_package(target,skin);verify_package(target,legacy)
    assert legacy['version']==version
    with zipfile.ZipFile(io.BytesIO(target)) as payload:updater=payload.read('GlamUpdater.exe')
    assert sha(updater)==metadata['updater_sha256']
    files={'SkinBlurSetup.exe':updater,'SkinBlur-update.json':(ROOT.parent/'updates/skin-blur.json').read_bytes(),'SkinBlur-'+version+'-Windows.zip':target}
    outer=io.BytesIO()
    with zipfile.ZipFile(outer,'w',zipfile.ZIP_STORED) as setup:
        for entry in metadata['outer_entries']:
            info=zipfile.ZipInfo(entry['filename'],tuple(entry['date_time']))
            for field in ('create_system','create_version','extract_version','internal_attr','external_attr'):setattr(info,field,entry[field])
            setup.writestr(info,files[entry['filename']])
    setup_bytes=outer.getvalue();assert sha(setup_bytes)==metadata['setup_sha256']
    url='https://github.com/'+REPO+'/releases/download/skin-blur-v'+version+'/SkinBlurSetup.exe'
    release=ensure_release('skin-blur-v'+version,'SkinVeil '+version+' · Skin Blur',
        '## 설치\n[설치프로그램]('+url+')을 실행해 업데이트를 내려받으세요. Adobe 작업을 저장하고 앱을 종료한 뒤 설치·Windows 관리자 승인을 진행하세요. 오프라인 설치는 Setup.zip을 풀고 안의 세 파일을 함께 둔 채 실행하세요.\n\n'+skin['notes']+
        '\n## 사용\n클립 선택 → SkinVeil 추가 → 효과 컨트롤에서 Skin Smoothing 조절. 기존 Skin Blur·Glam Local 프로젝트와 설치 위치를 유지합니다.\n\n## 검증 범위\n서로 크기가 다른 2·3·4명의 얼굴 검출과 각 얼굴의 블러·밝기 보정, 배포 DLL→worker 출력 일치, 배경·알파 보존을 로컬에서 검증했습니다. Premiere 실사용 확인은 별도입니다. Windows x64 · Premiere Pro 26 · SDR 8비트 · 최대 4명. 작은 얼굴·옆얼굴·가림에서 검출이 제한될 수 있으며 4K 전체 해상도 실시간 재생을 보장하지 않습니다.')
    upload(release,'SkinBlur-'+version+'-Windows.zip',target)
    upload(release,'SkinBlur-update.json',files['SkinBlur-update.json'])
    upload(release,'SkinBlur-'+version+'-Setup.zip',setup_bytes)
    upload(release,'SkinBlurSetup.exe',updater)
    migration=ensure_release('glam-v'+version,'SkinVeil '+version+' · 기존 업데이트 호환',
        '기존 Glam Local 업데이트 앱의 URL·파일명 호환을 위한 배포입니다. 실제 설치되는 제품은 SkinVeil (기존 Skin Blur)입니다.\n\n[새 설치](https://github.com/'+REPO+'/releases/tag/skin-blur-v'+version+')')
    upload(migration,'GlamLocal-'+version+'-Windows.zip',target)
    upload(migration,'GlamLocal-update.json',(ROOT.parent/'updates/glam.json').read_bytes())
    for info in (skin,legacy):
        verify_package(download(info['url']),info)
        print('PUBLIC_DOWNLOAD_VERIFIED',info['product'],info['version'],info['sha256'],flush=True)
    assert sha(download(url))==sha(updater)
    assert sha(download('https://github.com/'+REPO+'/releases/download/skin-blur-v'+version+'/SkinBlur-'+version+'-Setup.zip'))==sha(setup_bytes)
    result={'status':'complete','skin_version':version,'release':release['html_url'],'installer':url,'payload_sha256':sha(target),'installer_sha256':sha(updater),'signed_feeds_verified':2,'public_downloads_verified':4,'pin_feed_changed':False,'private_key_uploaded':False}
    path='distribution/skin-verification.json'
    try:old=api('/contents/'+path)
    except urllib.error.HTTPError as error:
        if error.code!=404:raise
        old=None
    body={'message':'Verify published multi-person skin update','content':base64.b64encode((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()).decode(),'branch':'main'}
    if old:body['sha']=old['sha']
    api('/contents/'+path,body,'PUT')
    print('SKIN_PUBLICATION_COMPLETE',flush=True)

# Github Action Trouble Shooting

깃허브 Action을 다루며 생기는 문제와 그에 대한 해결방법을 다룹니다.

## license

### serial

시리얼 번호는 

유니티id 웹사이트 - my account - my seat에 있다.

라이센스는

c:/programdata/unity 안에 있다.

## Deploy

```
Error: The deploy step encountered an error: The process '/usr/bin/git' failed with exit code 128 ❌
Deployment failed! ❌
```

해당 에러 발생 시 원인은 Workflow permission 설정이다. 디폴트 설정값이 read 만 허용이라서 gh-page 브랜치로 download가 안되는 모양이다. (혹은 깃허브 페이지에 업로드) write 권한까지 부여해주면(repo-setting-action-workflow에 read and write 허용 체크박스 존재) 해결된다.
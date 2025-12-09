INFO:     127.0.0.1:53605 - "POST /apps/api/benchmarks/upload HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 409, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\applications.py", line 1139, in __call__
    await super().__call__(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\applications.py", line 107, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    raise exc
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\cors.py", line 93, in __call__
    await self.simple_response(scope, receive, send, request_headers=headers)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\cors.py", line 144, in simple_response
    await self.app(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\routing.py", line 119, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\routing.py", line 105, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\routing.py", line 385, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\routing.py", line 284, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_backend\api\benchmarks.py", line 69, in upload_benchmark_file      
    current_user: User = await get_current_active_user()
                               ~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_backend\auth.py", line 120, in get_current_active_user
    if current_user.status != UserStatus.ACTIVE:
       ^^^^^^^^^^^^^^^^^^^

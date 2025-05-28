from backend.main import app

print("所有注册的路由：")
for route in app.routes:
    print(f"{route.path} - {route.methods}")
def start():
    import uvicorn

    uvicorn.run("auth_dock.main:app", host="127.0.0.1", port=8000)


def dev():
    import uvicorn

    uvicorn.run("auth_dock.main:app", host="127.0.0.1", port=8000, reload=True)

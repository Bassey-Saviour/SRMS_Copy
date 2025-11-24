#!/usr/bin/python3
import os
from utils import SESSION_COOKIE_NAME

def main():
    # Clear the session cookie and redirect to the site home
    target = '/public/index.html'
    # Expire the cookie immediately
    print('Status: 303 See Other')
    print(f'Location: {target}')
    print(f'Set-Cookie: {SESSION_COOKIE_NAME}=; HttpOnly; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
    print('Content-Type: text/html')
    print()
    print('<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={}"></head><body>'.format(target))
    # print('<p>Logged out. Redirecting...</p>')
    print('</body></html>')


if __name__ == '__main__':
    main()

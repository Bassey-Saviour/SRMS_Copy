import os
import time
import hmac
import hashlib
import base64
from http import cookies


def html_header(title="Result Management", extra_head=""):
      # Print the CGI content-type header and a minimal HTML header
      print("Content-Type: text/html\r\n\r\n")
      print("<!doctype html>")
      print("<html lang=\"en\">")
      print("<head>")
      print("  <meta charset=\"utf-8\">")
      print("  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">")
      print("  <link rel=\"icon\" type=\"image/png\" href=\"/public/images/results-icon-png-17974-removebg-preview.png\">")
      # include site stylesheet by default
      print("  <link rel=\"stylesheet\" href=\"/public/css/style.css\">")
      if extra_head:
            print(extra_head)
      print(f"  <title>{title}</title>")
      print("</head>")
      print("<body>")
      print("  <meta charset=\"utf-8\">")
      print("  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">")
      print(f"  <title>{title}</title>")
      print("</head>")
      print("<body>")


def html_footer():
	print("</body>")
	print("</html>")


# --- simple signed session cookie helpers ---
SESSION_SECRET = os.environ.get('SESSION_SECRET', 'dev-secret-change-me')
SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'session')


def _hmac(data: bytes) -> str:
      return hmac.new(SESSION_SECRET.encode('utf-8'), data, hashlib.sha256).hexdigest()


def create_session_cookie_value(student_id: str, max_age: int = 60 * 60 * 24):
      expiry = int(time.time()) + int(max_age)
      payload = f"{student_id}:{expiry}".encode('utf-8')
      b64 = base64.urlsafe_b64encode(payload).decode('utf-8')
      sig = _hmac(b64.encode('utf-8'))
      return f"{b64}.{sig}", max_age


def verify_session_cookie_value(cookie_value: str):
      try:
            parts = cookie_value.split('.')
            if len(parts) != 2:
                  return None
            b64, sig = parts
            expected = _hmac(b64.encode('utf-8'))
            if not hmac.compare_digest(expected, sig):
                  return None
            payload = base64.urlsafe_b64decode(b64.encode('utf-8')).decode('utf-8')
            student_id, expiry_s = payload.rsplit(':', 1)
            if int(expiry_s) < int(time.time()):
                  return None
            return student_id
      except Exception:
            return None


def parse_cookies():
      cookie_header = os.environ.get('HTTP_COOKIE', '')
      if not cookie_header:
            return {}
      c = cookies.SimpleCookie()
      c.load(cookie_header)
      return {k: v.value for k, v in c.items()}


def get_session_student_id():
      data = parse_cookies()
      val = data.get(SESSION_COOKIE_NAME)
      if not val:
            return None
      return verify_session_cookie_value(val)

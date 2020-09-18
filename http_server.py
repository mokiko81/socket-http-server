import socket
import sys
import traceback
import os
import mimetypes

DIRECTORY = 'webroot'

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    """
    return b"\r\n".join([
        b"HTTP/1.1 200 OK",
        b"Content-Type: " + mimetype,
        b"",
        body,
        ])

def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""
    return b"\r\n".join([
        b"HTTP/1.1 405 Method Not Allowed",
        b"",
        b"You can't do that on this server!",
        ])


def response_not_found():
    """Returns a 404 Not Found response"""
    return b"\r\n".join([
        b"HTTP/1.1 404 Not Found"])


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """
    method, path, version = request.split("\r\n")[0].split(" ")
    print('Method: {}\nPath: {}\nVersion: {}'.format(method, path, version))
    if method != "GET":
        raise NotImplementedError

    return path

def response_path(path):
    content = b"not implemented"
    mime_type = b"not implemented"

    path = DIRECTORY + path

    if path[-1] == '/':
        try:
            listings = os.listdir(path)
            content = bytes("\n".join(listings),'utf-8')
            mime_type = 'text/plain'
        except:
            raise NameError
    elif '.' not in path:
        try:
            path = path + '/'
            listings = os.listdir(path)
            content = bytes("\n".join(listings),'utf-8')
            mime_type = 'text/plain'
        except:
            raise NameError   
    else:
        try:
            in_file = open(path, 'rb')
            content = in_file.read()

            splitpath = path.split('/')
            file_name = splitpath[len(splitpath)-1]
            direc = path.strip(splitpath[len(splitpath)-1])
            mime_type = mimetypes.guess_type(file_name)[0]
        except:
            raise NameError

    return content, bytes(mime_type, 'utf-8')


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break
		

                print("Request received:\n{}\n\n".format(request))

                try:
                    path = parse_request(request)
                    content, mimetype = response_path(path)

                    print('Content: {}\nMimetype: {}\n'.format(content, mimetype))

                    response = response_ok(
                        body=content,
                        mimetype=mimetype
                    )


                except NotImplementedError:
                    response = response_method_not_allowed()
                except (NameError, FileNotFoundError):
                    response = response_not_found()

                conn.sendall(response)

            except:
                traceback.print_exc()
            finally:
                conn.close() 

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)



#!/usr/bin/env python3
"""Launch the completed bird-flu investigation locally without extra dependencies."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import webbrowser


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8083,
                        help='Local port (default: 8083; 0 chooses a free port)')
    parser.add_argument('--no-browser', action='store_true',
                        help='Print the address without opening a browser')
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    if not (directory / 'REPORT.html').is_file():
        parser.exit(1, 'Missing REPORT.html. Restore the completed research artifacts first.\n')
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    except (OSError, OverflowError) as error:
        parser.exit(1, f'Could not start local server: {error}\n'
                       'Try another port with --port 8084, or --port 0 for a free port.\n')
    with server:
        url = f'http://127.0.0.1:{server.server_port}/REPORT.html'
        print(f'Bird flu research demo: {url}', flush=True)
        print('Press Ctrl+C to stop. The saved report opens without rerunning the analysis.',
              flush=True)
        if not args.no_browser:
            Thread(target=webbrowser.open, args=(url,), daemon=True).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nStopped.')


if __name__ == '__main__':
    main()

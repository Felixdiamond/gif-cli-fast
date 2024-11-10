import argparse
import os
import signal
import sys
import time
from gif_cli_fast.load import load, _LOADERS
from gif_cli_fast.process import process, _PROCESSORS

def main():
    providers = list(_LOADERS.keys())
    modes = list(_PROCESSORS.keys())
    cols, rows = os.get_terminal_size()
    
    parser = argparse.ArgumentParser(epilog="https://github.com/telnet23/gif-cli-fast")
    parser.add_argument(
        "--provider",
        choices=providers,
        default=providers[0],
        help=f"provider to submit query to. {providers[0]} by default",
    )
    parser.add_argument(
        "--mode",
        choices=modes,
        default=modes[0],
        help=f"display mode. {modes[0]} by default. truecolor only supported on some terminals",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=cols,
        help="terminal size. determined automatically by default",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=rows,
        help="terminal size. determined automatically by default",
    )
    parser.add_argument(
        "--cache",
        default=os.path.join(os.getenv("HOME"), ".cache", "gif_cli_fast"),
        help="cache directory. determined automatically by default",
    )
    parser.add_argument(
        "--loops",
        type=int,
        default=0,
        help="number of times to loop the GIF. 0 for infinite (default)",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="query to submit to provider. a trending gif is returned by default",
    )
    
    args = parser.parse_args()
    
    content = load(args.provider, " ".join(args.query), args.cache)
    if content is None:
        print("No results", file=sys.stderr)
        sys.exit(1)
        
    signal.signal(signal.SIGINT, interrupt)
    print("\x1B[2J", end="", flush=True)
    print("\x1B[?25l", end="", flush=True)
    
    frames = process(content, (args.cols, args.rows), args.mode)
    loop_count = 0
    
    try:
        while args.loops == 0 or loop_count < args.loops:
            for output, duration in frames:
                print("\x1B[H", end="", flush=True)
                print(output, end="", flush=True)
                time.sleep(duration)
            loop_count += 1
    finally:
        print("\x1B[?25h", end="", flush=True)

def interrupt(_sig, _frame):
    print("\x1B[?25h", end="", flush=True)
    sys.exit(0)

if __name__ == "__main__":
    main()
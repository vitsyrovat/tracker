import argparse

from tracker.app import app
from tracker.models import db


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="track",
        description="Run the personal tracker Flask app.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    with app.app_context():
        db.create_all()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()


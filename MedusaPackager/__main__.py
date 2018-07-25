from MedusaPackager import processcli
import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--pytest":
        try:
            import pytest  # type: ignore
            sys.exit(pytest.main(sys.argv[2:]))
        except ImportError as e:
            print("Unable to run tests. Reason {}".format(e), file=sys.stderr)
            sys.exit(1)
    else:
        processcli.main()


if __name__ == '__main__':
    main()

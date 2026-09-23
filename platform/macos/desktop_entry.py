"""Dispatch bundled CLI workers before importing Cocoa (no extra windows)."""
import sys

from desktop_runtime import configure_runtime

configure_runtime()

if len(sys.argv) > 1 and sys.argv[1] == "--cli":
    from metacls.cli import main

    main(args=sys.argv[2:], prog_name="metacls")
else:
    from metacls_drop import main

    main()

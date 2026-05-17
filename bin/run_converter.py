import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from documents_utils.controllers.converter import main


def _silent_unraisable_hook(unraisable):
    # Supprime les PermissionError sur les fichiers temporaires Windows lors de l'arrêt
    if isinstance(unraisable.exc_value, PermissionError):
        return
    sys.__unraisablehook__(unraisable)


sys.unraisablehook = _silent_unraisable_hook

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if isinstance(e, PermissionError) and "Temp" in str(e):
            pass
        else:
            traceback.print_exc()
            sys.exit(1)

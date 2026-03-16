from pathlib import Path
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError


class Command(ScrapyCommand):
    """
    A custom command to clean the generated JSON files in the results directory.
    """

    requires_project = True

    def syntax(self):
        return ""

    def short_desc(self):
        return "Cleans the generated JSON files in the results_spiders directory"

    def run(self, args, opts):
        if args:
            raise UsageError("No arguments are accepted.", print_help=False)

        # Retrieves the output directory from settings or uses the fallback path
        output_dir = self.settings.get("OUTPUT_DIR")
        if not output_dir:
            base_dir = Path(__file__).resolve().parent.parent.parent
            output_dir = base_dir / "results_spiders"
        else:
            output_dir = Path(output_dir)

        if output_dir.exists() and output_dir.is_dir():
            files = list(output_dir.glob("*.json"))
            if not files:
                print(f"No JSON files found in {output_dir}")
                return

            for file in files:
                file.unlink()
            print(f"Successfully deleted {len(files)} file(s) from {output_dir}")
        else:
            print(f"Output directory {output_dir} does not exist.")

# gen-book-info

Fetches the data about a book specified by ISBN, and writes/prints in markdown format

```
usage: gen-book-info [-h] [--verbose] [--output {stdout,file,dir}]
                     [--path PATH]
                     isbn

fetch book info from ISBN and fills the template

positional arguments:
  isbn                  ISBN of the book. You may include hyphen, or strip
                        them.

options:
  -h, --help            show this help message and exit
  --verbose, -v
  --output, -o {stdout,file,dir}
                        output to: 'stdout': print to stdout (default) 'file':
                        writes to file (requires --path) 'dir': writes to a
                        file named with isbn under dir (--path or as specified
                        by $GEN_BOOK_INFO_DIR)
  --path PATH           write to this file (with --output file) or outdir
                        (with --output dir)
```

Examples:

- `gen-book-info isbn` -- writes to stdout. ISBN can be either 10 or 13 digits, and hyphen can be included or omitted.
- `gen-book-info isbn --output file --path /path/to/file.md` -- writes to `/path/to/file.md`
- `gen-book-info isbn --output dir --path /path/to/dir/` -- writes to `/path/to/dir/{isbn}.md`


If the files this script is about to write exists, it simply exits and refuses to overwrite the file.


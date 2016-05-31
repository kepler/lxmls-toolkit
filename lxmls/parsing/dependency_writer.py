from pathlib import Path


class DependencyWriter(object):
    """
    Dependency writer class
    """

    def __init__(self, parent_directory):
        if not isinstance(parent_directory, Path):
            parent_directory = Path(parent_directory)
        self.parent_directory = parent_directory

    def save(self, language, heads_pred):
        """Saves predicted dependency trees."""
        languages = ["danish", "dutch", "portuguese", "english"]
        if language not in languages:
            print("Language does not exist: \"%s\": Available are: %s" % (language, languages))
            return

        # Load test data
        n_toks = 0
        n_sents = 0
        with (self.parent_directory / (language + "_test.conll")).open(encoding='utf-8') as conll_file:
            with (self.parent_directory / (language + "_test.conll.pred")).open('w',
                                                                                encoding='utf-8') as conll_file_out:
                for line in conll_file:
                    line = line.rstrip()
                    if len(line) == 0:
                        n_toks = 0
                        n_sents += 1
                        conll_file_out.write(u"\n")
                        continue
                    fields = line.split("\t")

                    fields[6] = "{0}".format(heads_pred[n_sents][n_toks + 1])
                    line_out = "\t".join(fields)
                    n_toks += 1

                    conll_file_out.write(line_out)
                    conll_file_out.write(u"\n")

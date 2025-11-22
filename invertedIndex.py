import os
import re
import random
from typing import Optional
import zipfile


class InvertedIndex:
    def __init__(self):
        """Inverted index storing term -> posting list and ID mappings."""
        # {'unique_term': [internal_id_1, internal_id_5,...], ...}
        self._inverted_index: dict[str, list[int]] = {}
        # {internal_doc_id_1: original_doc_id,...}
        self._doc_id_map: dict[int, str] = {}
        # counter for internal_id
        self._next_internal_doc_id: int = 1
        # A dict to store the frequency for each term - {'term': doc_frequency, ...}
        self._docs_frequency: dict[str, int] = {}
        # Doc patterns
        self.doc_pattern = re.compile(r"<DOC>(.*?)</DOC>", re.DOTALL)
        self.doc_id_pattern = re.compile(r"<DOCNO>\s*(.*?)\s*</DOCNO>", re.DOTALL)
        self.text_pattern = re.compile(r"<TEXT>\s*(.*?)\s*</TEXT>", re.DOTALL)

    def build_index(self, data_dir: str = "data") -> None:
        """Build inverted index from AP data directory."""
        # Iterate over all .zip files in the directory
        for zip_name in os.listdir(data_dir):
            zip_path = os.path.join(data_dir, zip_name)
            print(f"Indexing file: {zip_name}")
            # Open the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Iterate over all files inside the zip
                for file_name in zip_ref.namelist():
                    with zip_ref.open(file_name) as file:
                        content = file.read().decode('latin-1')
                        docs = self.doc_pattern.findall(content)

                        for block in docs:
                            doc_id_match = self.doc_id_pattern.search(block)
                            text_match = self.text_pattern.search(block)

                            doc_id = doc_id_match.group(1).strip() if doc_id_match else None
                            text = text_match.group(1).strip() if text_match else ""

                            # Skip empty text
                            if not text:
                                continue

                            internal_id = self.__update_doc_id_map(doc_id)
                            tokens = text.split()  # simple whitespace tokenizer
                            self.__update_inverted_index(tokens, internal_id)
                    
        print("Finished indexing")

    def __update_doc_id_map(self, original_doc_id: Optional[str]) -> int:
        """Map original AP doc ID to internal numeric ID."""
        if original_doc_id is None:
            raise ValueError("Missing <DOCNO> tag in document.")

        assigned_id = self._next_internal_doc_id
        self._doc_id_map[assigned_id] = original_doc_id
        self._next_internal_doc_id += 1
        return assigned_id

    def __update_inverted_index(self, tokens: list[str], internal_id: int) -> None:
        """Insert terms into inverted index and update posting lists."""
        seen = set()

        for term in tokens:
            if term in seen:
                continue # avoid duplicates inside the same document
            seen.add(term)

            if term in self._inverted_index:
                self._inverted_index[term].append(internal_id)
            else:
                self._inverted_index[term] = [internal_id]

    def get_index(self) -> dict[str, list[int]]:
        """Return the inverted index."""
        return self._inverted_index

    def get_doc_id_map(self) -> dict[int, str]:
        """Return internal -> original document ID mapping."""
        return self._doc_id_map

    def sort_docs_frequency(self) -> None:
        """Sort term dictionary by document frequency (descending)."""
        for term, postings_list in self._inverted_index.items():
            self._docs_frequency[term] = len(postings_list)

        self._docs_frequency = dict(
            sorted(self._docs_frequency.items(), key=lambda x: x[1], reverse=True)
        )

    def get_top_10_terms(self) -> list[tuple[str, int]]:
        """Return the top 10 highest-frequency terms."""
        return list(self._docs_frequency.items())[:10]

    def get_lowest_10_terms(self) -> list[tuple[str, int]]:
        """Return the lowest 10 frequency terms."""
        return list(self._docs_frequency.items())[-10:]

    def find_similar_terms(self) -> dict | None:
        """Find two alphabetic terms sharing the same postings list."""
        # Use reversed inverted index (hashmap for quick lookup):
        # Key = tuple(sorted doc_ids), Value = first found alphabetic term
        reversed_inverted_index = {}

        for term, postings_list in self._inverted_index.items():
            if not term.isalpha():
                continue  # skip non-alphabetic terms (for more meaningful results)

            if len(postings_list) < 20 or len(postings_list) > 100:
                continue  # skip too small or too large postings lists

            postings_tuple = tuple(postings_list)  # lists not hashable -> use tuple

            if postings_tuple not in reversed_inverted_index:
                reversed_inverted_index[postings_tuple] = term

            # Found a second term with the same postings list
            elif term != reversed_inverted_index[postings_tuple]:
                internal_ids = list(postings_tuple)
                original_ids = [self._doc_id_map[i] for i in internal_ids]

                return {
                    "terms": (reversed_inverted_index[postings_tuple], term),
                    "internal_ids": internal_ids,
                    "original_ids": original_ids
                }
            
        # If no pair found
        return None


if __name__ == "__main__":
    # Build inverted index
    index = InvertedIndex()
    index.build_index()

    # Retrieve data structures
    revert_index = index.get_index()
    doc_mapper = index.get_doc_id_map()

    # Print first 10 terms for inspection
    first_keys = list(revert_index.keys())[:10]
    for key in first_keys:
        values = revert_index[key]
        print(key, values[:10])

    # Collection statistics
    index.sort_docs_frequency()
    print(index.get_top_10_terms())
    print(index.get_lowest_10_terms())

    # Similar term detection
    print(index.find_similar_terms())

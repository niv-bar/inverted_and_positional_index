# Libraries
import os
import re
import random
from typing import Optional

class BooleanRetrieval:
    """
    Boolean retrieval model supporting AND, OR, and AND-NOT operations (Part 2)
    Complexity: O(N+M)
    """
    def __init__(self):
        pass

    # AND
    @staticmethod
    def __intersect(l1_ids: list[int], l2_ids: list[int]) -> list[int]:
        """Return intersection (AND) of two sorted posting lists."""
        intersection = []
        i = j = 0

        while i < len(l1_ids) and j < len(l2_ids):
            if l1_ids[i] == l2_ids[j]:
                intersection.append(l1_ids[i])
                i += 1
                j += 1

            elif l1_ids[i] < l2_ids[j]:
                i += 1

            else:
                j += 1

        return intersection

    # OR
    @staticmethod
    def __union(l1_ids: list[int], l2_ids: list[int]) -> list[int]:
        """Return union (OR) of two sorted posting lists."""
        union_result = []
        i = j = 0

        while i < len(l1_ids) and j < len(l2_ids):

            if l1_ids[i] == l2_ids[j]:
                union_result.append(l1_ids[i])
                i += 1
                j += 1

            elif l1_ids[i] < l2_ids[j]:
                union_result.append(l1_ids[i])
                i += 1

            else:
                union_result.append(l2_ids[j])
                j += 1

        # Append remaining elements
        while i < len(l1_ids):
            union_result.append(l1_ids[i])
            i += 1

        while j < len(l2_ids):
            union_result.append(l2_ids[j])
            j += 1

        return union_result

    # AND NOT
    @staticmethod
    def __difference(l1_ids: list[int], l2_ids: list[int]) -> list[int]:
        """Return difference (r1 AND NOT r2) between two sorted posting lists."""
        difference_result = []
        i = j = 0

        while i < len(l1_ids) and j < len(l2_ids):
            if l1_ids[i] == l2_ids[j]:
                i += 1
                j += 1

            elif l1_ids[i] < l2_ids[j]:
                difference_result.append(l1_ids[i])
                i += 1

            else:
                j += 1

        # Append remaining elements in l1
        while i < len(l1_ids):
            difference_result.append(l1_ids[i])
            i += 1

        return difference_result

    def retrieve(
        self,
        inverted_index: dict[str, list[int]],
        doc_map: dict[int, str],
        query_file_path: str = "data/BooleanQueries.txt",
        output_file_path: str = "Part_2.txt"
    ) -> None:
        """Evaluate Boolean RPN queries and write matching document IDs to file."""

        operators = {"AND", "OR", "NOT"} # Allowed Boolean operators

        # Open file (Part_2) for writing
        with open(output_file_path, "w", encoding="utf-8") as out_f:

            # Open queries file
            with open(query_file_path, "r", encoding="utf-8") as in_f:
                # Break into lines
                lines = [line.strip() for line in in_f]

            # Iterate each line
            for line in lines:
                # Skip empty lines
                if not line:
                    continue

                # Tokenize the current query
                tokens = line.split()
                # New stack for each query
                stack = []

                # Iterate each token in the query
                for token in tokens:
                    # if token is a term
                    if token not in operators:
                        # get the posting list of the relevant term and append it to the stack
                        postings_ids = inverted_index.get(token, [])
                        stack.append(postings_ids)

                    # if token is an operator
                    else:
                        # Retrieve the posting lists in reverse order
                        # Right operand
                        r2 = stack.pop()
                        # Left Operand
                        r1 = stack.pop()

                        result = []
                        # Apply the required operator logic
                        # AND
                        if token == "AND":
                            result = self.__intersect(r1, r2)
                        # OR
                        elif token == "OR":
                            result = self.__union(r1, r2)
                        # r1 AND NOT r2
                        elif token == "NOT":
                            result = self.__difference(r1, r2)

                        # Push the result list into the stack
                        stack.append(result)

                # Retrieve the final result list
                final_internal_ids = stack.pop()

                # Convert internal_ids into original_ids
                original_ids = [doc_map[internal_id] for internal_id in final_internal_ids]

                # Write a line in the open file (a single query)
                output_line = " ".join(original_ids)
                out_f.write(output_line + "\n")


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

    def build_index(self, data_dir: str = "data/docs") -> None:
        """Build inverted index from AP data directory."""

        doc_pattern = re.compile(r"<DOC>(.*?)</DOC>", re.DOTALL)
        doc_id_pattern = re.compile(r"<DOCNO>\s*(.*?)\s*</DOCNO>", re.DOTALL)
        text_pattern = re.compile(r"<TEXT>\s*(.*?)\s*</TEXT>", re.DOTALL)

        for root, dirs, files in os.walk(data_dir):
            for file in files:
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="latin1") as f:
                    content = f.read()

                docs = doc_pattern.findall(content)

                for block in docs:
                    doc_id_match = doc_id_pattern.search(block)
                    text_match = text_pattern.search(block)

                    doc_id = doc_id_match.group(1).strip() if doc_id_match else None
                    text = text_match.group(1).strip() if text_match else ""

                    # Skip empty text
                    if not text:
                        continue

                    internal_id = self.__update_doc_id_map(doc_id)
                    tokens = self.__tokenize(text)
                    self.__update_inverted_index(tokens, internal_id)

    def __update_doc_id_map(self, original_doc_id: Optional[str]) -> int:
        """Map original AP doc ID to internal numeric ID."""
        if original_doc_id is None:
            raise ValueError("Missing <DOCNO> tag in document.")

        assigned_id = self._next_internal_doc_id
        self._doc_id_map[assigned_id] = original_doc_id
        self._next_internal_doc_id += 1
        return assigned_id

    @staticmethod
    def __tokenize(text: str) -> list[str]:
        """Tokenize text into alphanumeric terms."""
        if not text:
            return []
        return re.findall(r"\b\w+\b", text)

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
        reversed_inverted_index = {}

        # Step 1: Reverse the inverted index:
        # Key = tuple(sorted doc_ids), Value = list of terms sharing this postings list
        for term, postings_list in self._inverted_index.items():
            postings_tuple = tuple(postings_list)  # lists not hashable -> use tuple

            if postings_tuple not in reversed_inverted_index:
                reversed_inverted_index[postings_tuple] = [term]
            else:
                reversed_inverted_index[postings_tuple].append(term)

        # Step 2: Look for a postings list that belongs to at least two different terms
        for postings_tuple, terms in reversed_inverted_index.items():
            # keep only alphabetic words (no pure numbers) - not necessary, doing that from the reason we want words terms
            word_terms = [t for t in terms if t.isalpha()]

            # require: at least 2 valid words + more than 1 document (adjusting the threshold to 20 docs to have good representation)
            if len(word_terms) >= 2 and len(postings_tuple) > 20:
                # randomly pick 2 distinct terms
                term1, term2 = random.sample(word_terms, 2)

                internal_ids = list(postings_tuple)
                original_ids = [self._doc_id_map[i] for i in internal_ids]

                return {
                    "terms": (term1, term2),
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

    # Boolean retrieval
    bool_retrieval = BooleanRetrieval()
    bool_retrieval.retrieve(revert_index, doc_mapper)

    # Collection statistics
    index.sort_docs_frequency()
    print(index.get_top_10_terms())
    print(index.get_lowest_10_terms())

    # Similar term detection
    print(index.find_similar_terms())

import os
import re
from collections import Counter


class InvertedIndex:
    def __init__(self):
        # {'unique_term': [(internal_id, term_frequency)], ...}
        self._inverted_index = {}
        # {'internal_doc_id_1': original_doc_id,...}
        self._doc_id_map = {}
        # counter for internal_id
        self._next_internal_doc_id = 1

    def build_index(self, data_dir: str = "data/docs"):
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
                    frequency = self.__tokenize_and_count(text)
                    self.__update_inverted_index(frequency, internal_id)

    def __update_doc_id_map(self, original_doc_id):
        assigned_id = self._next_internal_doc_id
        self._doc_id_map[assigned_id] = original_doc_id
        self._next_internal_doc_id += 1
        return assigned_id

    @staticmethod
    def __tokenize_and_count(text):
        if not text:
            return Counter()

        tokens = re.findall(r"\b\w+\b", text)
        return Counter(tokens)

    def __update_inverted_index(self, doc_frequencies, internal_id):

        for term, freq in doc_frequencies.items():
            if term in self._inverted_index:
                self._inverted_index[term].append((internal_id, freq))
            else:
                self._inverted_index[term] = [(internal_id, freq)]

    def get_index(self):
        return self._inverted_index

    def get_doc_id_map(self):
        return self._doc_id_map

    #=== task 2 ====
    # O(N+M)
    # AND
    @staticmethod
    def __intersect(l1, l2):
        intersection = []
        i = j = 0

        while i < len(l1) and j < len(l2):
            if l1[i][0] == l2[j][0]:
                intersection.append((l1[i][0]))
                i += 1
                j += 1
            elif l1[i][0] < l2[j][0]:
                i += 1
            else:
                j += 1

        return intersection

    # OR
    @staticmethod
    def __union(l1, l2):
        union_result = []
        i = j = 0

        while i < len(l1) and j < len(l2):
            doc_id_l1 = l1[i][0]
            doc_id_l2 = l2[j][0]

            if doc_id_l1 == doc_id_l2:
                union_result.append((l1[i][0]))
                i += 1
                j += 1

            elif doc_id_l1 < doc_id_l2:
                union_result.append((l1[i][0]))
                i += 1

            else:  # doc_id_l1 > doc_id_l2
                union_result.append((l2[j][0]))
                j += 1

        if i < len(l1):
            while i < len(l1):
                union_result.append((l1[i][0]))
                i += 1

        if j < len(l2):
            while j < len(l2):
                union_result.append((l2[j][0]))
                j += 1

        return union_result

    # AND NOT
    @staticmethod
    def __difference(l1, l2):
        difference_result = []
        i = j = 0

        while i < len(l1) and j < len(l2):
            doc_id_l1 = l1[i][0]
            doc_id_l2 = l2[j][0]

            if doc_id_l1 == doc_id_l2:
                 i += 1
                 j += 1

            elif doc_id_l1 < doc_id_l2:
                difference_result.append((l1[i][0]))
                i += 1

            else:  # doc_id_l1 > doc_id_l2
                j += 1

        if i < len(l1):
            while i < len(l1):
                difference_result.append((l1[i][0]))
                i += 1

        return difference_result

    def retrieve(self, query_file_path="data/BooleanQueries.txt", output_file_path="Part_2.txt"):
        """
        קורא שאילתות RPN מקובץ, מעבד אותן, וממיר את התוצאות ל-Original IDs,
        אותם הוא כותב לקובץ פלט.
        """
        # קבוצת האופרטורים המותרים
        operators = {"AND", "OR", "NOT"}

        # פותחים את קובץ הפלט לכתיבה
        with open(output_file_path, "w", encoding="utf-8") as out_f:

            # פותחים את קובץ השאילתות לקריאה
            with open(query_file_path, "r", encoding="utf-8") as in_f:
                lines = [line.strip() for line in in_f]

            # 1. עוברים על כל שאילתה (שורה)
            for line in lines:
                if not line:  # מדלגים על שורות ריקות
                    continue

                tokens = line.split()  # פיצול השאילתה לאסימונים
                stack = []  # 2. אתחול מחסנית חדשה לכל שאילתה

                # 3. עוברים על כל אסימון בשאילתה
                for token in tokens:

                    if token not in operators:
                        # 4. אם האסימון הוא מונח (Term)

                        # נשלוף את רשימת הפרסומים (שמכילה זוגות של (id, tf))
                        postings_with_tf = self._inverted_index.get(token, [])

                        # נחלץ רק את ה-Internal IDs (האיבר הראשון ב-Tuple)
                        postings_ids = [doc[0] for doc in postings_with_tf]

                        # נדחוף את רשימת ה-IDs למחסנית
                        stack.append(postings_ids)

                    else:
                        # 5. אם האסימון הוא אופרטור

                        # שלוף את שני האופרנדים האחרונים (בסדר הפוך)
                        R2 = stack.pop()  # אופרנד ימני (או הרשימה ל-NOT)
                        R1 = stack.pop()  # אופרנד שמאלי

                        result = []
                        if token == "AND":
                            result = self.__intersect(R1, R2)
                        elif token == "OR":
                            result = self.__union(R1, R2)
                        elif token == "NOT":
                            # כפי שנדרש: R1 AND NOT R2 (כלומר, R1 פחות R2)
                            result = self.__difference(R1, R2)

                        # דחוף את התוצאה חזרה למחסנית
                        stack.append(result)

                # 6. סיום עיבוד השאילתה
                # התוצאה הסופית (רשימת Internal IDs) נמצאת בראש המחסנית
                final_internal_ids = stack.pop()

                # 7. המרת Internal IDs ל-Original IDs
                original_ids = [self._doc_id_map[internal_id] for internal_id in final_internal_ids]

                # 8. כתיבה לקובץ הפלט בפורמט הנדרש (רווחים בין המזהים)
                output_line = " ".join(original_ids)
                out_f.write(output_line + "\n")

        print(f"עיבוד בוליאני הושלם. התוצאות נשמרו ב: {output_file_path}")




if __name__ == "__main__":
    index = InvertedIndex()
    # index.build_index()
    # store = index.get_index()
    #
    # first_keys = list(store.keys())[:10]
    # print(first_keys)

    index.retrieve()






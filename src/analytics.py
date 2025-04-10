from collections import Counter

class MessageAnalytics:
    def __init__(self):
        self.word_counts = Counter()

    def analyze_message(self, text):
        """Xabarni tahlil qilib, so‘zlar sonini yangilaydi"""
        if not text or text == "Bo‘sh xabar":
            return
        words = text.lower().split()
        self.word_counts.update(words)

    def get_top_words(self, limit=5):
        """Eng ko‘p ishlatilgan so‘zlarni qaytaradi"""
        return self.word_counts.most_common(limit)

    def print_stats(self):
        """Tahlil natijalarini konsolda chiqaradi"""
        top_words = self.get_top_words()
        if top_words:
            print("\nEng ko‘p ishlatilgan so‘zlar:", flush=True)
            for word, count in top_words:
                print(f"  {word}: {count} marta", flush=True)
        else:
            print("Hali tahlil qiladigan ma'lumot yo‘q", flush=True)
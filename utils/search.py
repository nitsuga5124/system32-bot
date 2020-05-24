class Result(object):
	def __init__(self, term, comparison, case_sensitive=False):
		self.term = term
		self.comparison = comparison
		self.case_sensitive = case_sensitive
		self._calculate_units()

	def _calculate_units(self):
		most_matches = 0

		for idx in range(len(self.comparison)):
			matches = 0
			term = self.term if self.case_sensitive else self.term.lower()
			comparison = (self.comparison if self.case_sensitive else self.comparison.lower())[idx:]

			for idx2 in range(min(len(term), len(comparison))):
				if term[idx2] == comparison[idx2]:
					matches += 1

			if matches > most_matches:
				most_matches = matches

		self.matches = most_matches
		self.containment = most_matches / min(len(self.term), len(self.comparison))
		self.similarity = most_matches / max(len(self.term), len(self.comparison))
		self.average = (self.containment + self.similarity) / 2
		self.strength = (self.containment + self.average) / 2

	def __str__(self, /):
		return self.comparison

	def __repr__(self, /):
		return f"<Result comparison={repr(self.comparison)} matches={repr(self.matches)} containment={repr(self.containment)} similarity={repr(self.similarity)} average={repr(self.average)} strength={repr(self.strength)}>"

	def __int__(self, /):
		return int(self.strength)

	def __float__(self, /):
		return float(self.strength)

	def __round__(self, /):
		return float(self.strength)

	def __eq__(self, value, /):
		return self.comparison == value.comparison

	def __ne__(self, value, /):
		return self.comparison != value.comparison


class Search(object):
	def __init__(self, term, comparisons, *, case_sensitive=False):
		self.term = term
		self.comparisons = comparisons
		self._matches = [Result(term, c, case_sensitive) for c in comparisons]

	@property
	def matches(self):
		return self._matches

	def best(self, min_accuracy=.7):
		def _strength_check(value):
			return value.strength >= min_accuracy and value.strength >= strength_boundary

		def _average_check(value):
			return value.average >= min_accuracy and value.average >= strength_boundary
			
		def _containment_check(value):
			return value.containment >= min_accuracy and value.containment >= strength_boundary

		strength_boundary = max([m.strength for m in self.matches]) * .75
		best = list(filter(_strength_check, self.matches))

		if not len(best):
			return None

		elif len(best) == 1:
			return best[0]

		best = list(filter(_containment_check, best))

		if len(best) == 1:
			return best[0]

		else:
			return None

	def top(self, limit=1):
		return sorted(self.matches, key=lambda m: m.strength, reverse=True)[:limit]

	def bottom(self, limit=1):
		return sorted(self.matches, key=lambda m: m.strength, reverse=True)[-limit:]

	def range(self, min, max):
		return sorted(self.matches, key=lambda m: m.strength, reverse=True)[min:max]

	def accurate_to(self, accuracy):
		return sorted([m for m in self.matches if m.strength >= accuracy], key=lambda m: m.strength, reverse=True)

	def __str__(self, /):
		return self.term

	def __repr__(self, /):
		return f"<Search term={repr(self.term)} comparisons={repr(len(self.comparisons))}>"

	def __int__(self, /):
		return int(self.matches)

	def __round__(self, /):
		return round(self.matches)

	def __float__(self, /):
		return self.matches
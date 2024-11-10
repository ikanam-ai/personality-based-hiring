import pandas as pd
from scipy.optimize import minimize


class MBTIConverter:
    def __init__(self, matrix_path: str = "data/ocean_mbti.csv"):
        self.correlation_matrix = pd.read_csv(matrix_path, index_col=0)
        # Bounds for OCEAN values (0.0 to 1.0)
        self.bounds = [(0.0, 1.0)] * 5
        self.mbti_ranges = self.calculate_mbti_score_range()

    # Function to calculate the MBTI score for a given dichotomy and OCEAN values
    def mbti_score(self, dichotomy, ocean_values):
        return sum(
            self.correlation_matrix.loc[dichotomy, trait] * ocean_values[trait]
            for trait in ocean_values
        )

    # Define the objective function for optimization (negative for maximization)
    def objective_function(self, ocean_array, dichotomy, maximize=False):
        ocean_values = {
            "extraversion": ocean_array[0],
            "openness": ocean_array[1],
            "agreeableness": ocean_array[2],
            "conscientiousness": ocean_array[3],
            "neuroticism": ocean_array[4],
        }
        score = self.mbti_score(dichotomy, ocean_values)
        return -score if maximize else score

    # Function to calculate min and max MBTI scores for each dichotomy using optimization
    def calculate_mbti_score_range(self):
        mbti_ranges = {}
        for dichotomy in self.correlation_matrix.index:
            # Find the minimum score
            min_result = minimize(
                self.objective_function,
                [0.5] * 5,
                args=(dichotomy, False),
                bounds=self.bounds,
            )
            min_score = self.mbti_score(
                dichotomy,
                dict(
                    zip(
                        [
                            "extraversion",
                            "openness",
                            "agreeableness",
                            "conscientiousness",
                            "neuroticism",
                        ],
                        min_result.x,
                    )
                ),
            )

            # Find the maximum score
            max_result = minimize(
                self.objective_function,
                [0.5] * 5,
                args=(dichotomy, True),
                bounds=self.bounds,
            )
            max_score = self.mbti_score(
                dichotomy,
                dict(
                    zip(
                        [
                            "extraversion",
                            "openness",
                            "agreeableness",
                            "conscientiousness",
                            "neuroticism",
                        ],
                        max_result.x,
                    )
                ),
            )

            mbti_ranges[dichotomy] = (
                min(min_score, max_score),
                max(min_score, max_score),
            )  # Ensure min and max are ordered

        return mbti_ranges

    # Convert OCEAN values to MBTI type
    def convert_ocean_to_mbti(self, ocean_values):
        mbti_scores = {}
        mbti_dichotomies = self.correlation_matrix.index

        # Calculate MBTI scores based on input OCEAN values
        for dichotomy in mbti_dichotomies:
            mbti_scores[dichotomy] = self.mbti_score(dichotomy, ocean_values)
        # Determine MBTI type based on whether scores are above or below the midpoint of their range
        mbti_type = []
        for dichotomy in mbti_dichotomies:
            min_score, max_score = self.mbti_ranges[dichotomy]
            midpoint = (min_score + max_score) / 2

            if mbti_scores[dichotomy] > midpoint:
                if dichotomy == "E-I":
                    mbti_type.append("I")
                elif dichotomy == "S-N":
                    mbti_type.append("N")
                elif dichotomy == "T-F":
                    mbti_type.append("F")
                elif dichotomy == "J-P":
                    mbti_type.append("P")
            else:
                if dichotomy == "E-I":
                    mbti_type.append("E")
                elif dichotomy == "S-N":
                    mbti_type.append("S")
                elif dichotomy == "T-F":
                    mbti_type.append("T")
                elif dichotomy == "J-P":
                    mbti_type.append("J")

        return "".join(mbti_type)

    def get_ocean_values(self, dict_ocean):
        ocean_vars = [
            "extraversion",
            "openness",
            "agreeableness",
            "conscientiousness",
            "neuroticism",
        ]
        return {k: dict_ocean[k] for k in ocean_vars}


converter = MBTIConverter()

# Calculate MBTI score ranges
converter.calculate_mbti_score_range()

# Example OCEAN values (from 0.0 to 1.0)
example_ocean = {
    "extraversion": 0.9,
    "openness": 0.9,
    "agreeableness": 0.9,
    "conscientiousness": 0.9,
    "neuroticism": 0.9,
}


# Convert OCEAN to MBTI
mbti_result = converter.convert_ocean_to_mbti(example_ocean)
print("MBTI Type:", mbti_result)

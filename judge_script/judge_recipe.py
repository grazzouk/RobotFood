import argparse

class RecipeParser:

    def __init__(self, filepath, csv):
        self.filepath = filepath
        self.csv = csv
        self.recps_with_score = []

    def _parse_ingredients(self, section):
        ingredients = {}
        ingredients_list = section.split("\n")[1:]
        # assumes core ingredient is last word before first comma
        for ingredient in ingredients_list:
            ingredient = ingredient.split(",")[0].split("(")[0].split()
            ingredients[ingredient[-1]] = False
        return ingredients

    def _parse_method(self, section, ingredients):
        score = 0
        if len(ingredients) == 0:
            score -= 50
        preheated = False
        steps = section.split("\n")
        for step in steps:
            # if step is shorter than 5 words the nn probably wrote an ingredients list in the method.
            if len(step.split()) < 5:
                score -= 50
                continue

            # check if oven is preheated multiple times
            if "preheat" in step:
                if preheated:
                    score -= 25
                else:
                    preheated = True
            else:
                if len(ingredients) == 0:
                    continue
                for ingredient, used in ingredients.items():
                    if ingredient == used:
                        return
                    if ingredient in step.split():
                        score += 30

        for used in ingredients.values():
            if not used:
                score -= 10

        return score

    def _parse_recipe(self, recp):
        score = 1000
        sections = recp.split("\n\n")

        # points lost for not having all sections (or having too many)
        if len(sections) != 3:
            score -= 100

        title = sections[0].strip()

        # return if title is too long
        if len(title.split()) > 10:
            return

        # Check if recp sections
        ingredients = {}
        for section in sections:
            method_handled = False;
            if "ingredients:" in section.lower():
                ingredients = self._parse_ingredients(section.lower())

            elif "method:" in section.lower():
                if method_handled:
                    score -= 150
                    continue
                score += self._parse_method(section.lower(), ingredients)
                method_handled = True;

        # check title
        for ingredient in ingredients:
            if ingredient in title:
                score += 150

        # handle multiple recipes with same title
        titlenumber = 2
        existing_titles = [et for et, _, _ in self.recps_with_score]
        if title in existing_titles:
            title += " {}".format(titlenumber)

        while title in existing_titles:
            titlenumber += 1
            title = "{}{}".format(title[:-1], titlenumber)

        self.recps_with_score.append((title, score, recp))

    def _check_first(self, recp):
        recp_elems = recp.split("\n\n")
        # return if first recp is too short
        if len(recp_elems) == 1:
            return

        # or if "title" is too long (means we're in the middle of a list of ingredients) or empty
        title_len = len(recp_elems[0].split())
        if title_len == 0 or title_len > 10:
            return

        # then parse normally
        self._parse_recipe(recp)

    def review_text(self):
        with open(self.filepath, encoding="utf-8") as f:
            recps = f.read()
        # Split file into separate recipes
        recps_list = recps.split("\n\n\n")
        # process first recipe (separate handling since it may be incomplete)
        self._check_first(recps_list[0])
        # Then process rest of the elements
        for recp in recps_list[1:]:
            self._parse_recipe(recp)

        # Sort, print, and if required save.
        output_string = ""
        for title, score, recp in sorted(self.recps_with_score, key=lambda x: x[1], reverse=True):
            print("Title: {}       Score: {}".format(title, score))
            if self.csv is not None:
                output_string += '"{}","{}","{}"\n'.format(title, score, recp)
        if self.csv is not None:
            with open(self.csv, "w",  encoding="utf-8") as outfile:
                outfile.write(output_string)


def parse_args():
    parser = argparse.ArgumentParser(description='Judge a group of recipes based on their accuracy to real recipes.')
    parser.add_argument('file',
                        help='the file containing the recipes')
    parser.add_argument('--csv', default=None,
                        help='a csv output file containing recipe titles and scores')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rp = RecipeParser(args.file, args.csv)
    rp.review_text()

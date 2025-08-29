# phoneme sets
C = ["m","n","ng","p","t","k","b","d","g","f","s","h","l"]
G = ["w","y"]
V = ["e","i","a","o","ō","u", "ə"]
F = ["p","t","k","m","n","ng","l"]

C_block = C + G + [c+g for c in C for g in G]  # C, G, or C+G
V_block = V + [v+f for v in V for f in F]     # V or V+F

def expand_syllable(syllables):
    new_syllables = []
    for syl in syllables:
        first_letter = syl[0]

        if first_letter in V:
            for b in C_block:
                new_syllables.append(b + syl)
        elif first_letter in G or first_letter in C:
            for b in V_block:
                new_syllables.append(b + syl)
        else:
            new_syllables.append(syl)
    return new_syllables

def generate_words(start_syllables, iterations):
    current_syllables = start_syllables[:]
    for _ in range(iterations):
        current_syllables = expand_syllable(current_syllables)
    return current_syllables

start = ["ə"] 
all_words = generate_words(start, 2)  
for word in all_words:
    print(word)

# phoneme sets
C = ("m","n","ng","p","t","k","b","d","g","f","s","h","l")
G = ("w","y")
V = ("e","i","a","o","ō","u","ə")
F = ("p","t","k","m","n","ng","l")

C_block = C + G + tuple(c+g for c in C for g in G)  # C, G, or C+G
V_block = V + tuple(v+f for v in V for f in F)     # V or V+F

# build a master alphabet order
alphabet = C + G + V  # base symbols only
order = {sym: i for i, sym in enumerate(alphabet)}

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

def generate_words(syllables, iterations):
    for _ in range(iterations):
        syllables = expand_syllable(syllables)
    return syllables

def sort_key(word):
    """convert word into tuple of ranks for sorting"""
    key = []
    i = 0
    while i < len(word):
        # check for digraphs like "ng" or long symbols like "ō"
        if (k := order.get(word[i:i+2])) is not None:  
            key.append(k)
            i += 2
        elif (k := order.get(word[i])) is not None:
            key.append(k)
            i += 1
        else:
            # fallback: put unknowns at end
            key.append(len(order))
            i += 1
    return tuple(key)

start = ["ə"]
all_words = generate_words(start, 2)

# sort using custom alphabet
all_words_sorted = sorted(all_words, key=sort_key)

for word in all_words_sorted:
    print(word)

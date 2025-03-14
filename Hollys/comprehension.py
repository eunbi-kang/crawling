








if __name__ == "__main__":
    numbers = range(100)
    volume = ['홀수' if num % 2 != 0 else '짝수' for num in numbers]

    subjects = ["국어", "영어", "수학"]
    scores = [90, 87, 91]


    # john = {key: 'A' if value >= 90 else 'B' for key, value in zip(subjects, scores)}
    john = {subject: grade for subject, grade in [(sub, 'A' if score >= 90 else 'B') for sub, score in zip(subjects, scores)]}

    print(john)

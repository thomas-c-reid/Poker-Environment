import shortuuid
import random
from env.enums import BettingStagesEnum

def generate_shortuuid_id(length=4):
    uuid = shortuuid.uuid()
    return uuid[:length]

def playerNameGenerator():
    names = [
        "Aaron", "Abby", "Adam", "Adrian", "Aiden", "Alex", "Alexa", "Alice", "Alicia", "Amanda",
        "Amber", "Amy", "Andrew", "Angela", "Anna", "Anthony", "April", "Arthur", "Ashley", "Austin",
        "Barbara", "Ben", "Beth", "Blake", "Bobby", "Brad", "Brandon", "Brenda", "Brian", "Brittany",
        "Brooke", "Caleb", "Cameron", "Carl", "Carmen", "Carol", "Catherine", "Chad", "Charles", "Cheryl",
        "Chris", "Christina", "Christopher", "Cindy", "Claire", "Colin", "Connor", "Corey", "Crystal", "Cynthia",
        "Daniel", "David", "Debbie", "Dennis", "Diana", "Diane", "Dylan", "Edward", "Eileen", "Elaine",
        "Elizabeth", "Ellen", "Emily", "Emma", "Eric", "Erica", "Ethan", "Eva", "Evan", "Evelyn",
        "Frank", "Gabriel", "Gary", "George", "Gina", "Grace", "Greg", "Hannah", "Heather", "Holly",
        "Ian", "Isaac", "Jack", "Jacob", "James", "Jamie", "Jane", "Janet", "Jason", "Jean",
        "Jeff", "Jennifer", "Jeremy", "Jerry", "Jesse", "Jessica", "Jill", "Joan", "Joe", "John",
        "Jonathan", "Jordan", "Joseph", "Joshua", "Joyce", "Judith", "Judy", "Julia", "Justin", "Karen",
        "Katherine", "Kathleen", "Katie", "Kayla", "Keith", "Kelly", "Ken", "Kenneth", "Kevin", "Kim",
        "Kimberly", "Kyle", "Laura", "Lauren", "Lena", "Leo", "Leonard", "Liam", "Linda", "Lisa",
        "Logan", "Lori", "Luke", "Madison", "Maggie", "Margaret", "Maria", "Marie", "Mark", "Martha",
        "Martin", "Mary", "Mason", "Matt", "Matthew", "Megan", "Melanie", "Melissa", "Michael", "Michelle",
        "Mike", "Molly", "Nancy", "Natalie", "Nathan", "Nathaniel", "Neil", "Nicholas", "Nicole", "Noah",
        "Olivia", "Pamela", "Patricia", "Patrick", "Paul", "Peter", "Philip", "Rachel", "Rebecca", "Richard",
        "Robert", "Roger", "Ronald", "Rose", "Russell", "Ryan", "Samantha", "Samuel", "Sandra", "Sara",
        "Sarah", "Scott", "Sean", "Shane", "Sharon", "Sheila", "Sophia", "Spencer", "Stephanie", "Stephen",
        "Steve", "Steven", "Susan", "Sydney", "Taylor", "Teresa", "Thomas", "Tiffany", "Tim", "Timothy",
        "Tyler", "Vanessa", "Veronica", "Victoria", "Vincent", "Virginia", "Walter", "Wendy", "William", "Zachary"
    ]
    return random.choice(names)

def increase_betting_round(betting_stage: BettingStagesEnum):
    """
    Increase the betting stage
    """
    if betting_stage == BettingStagesEnum.PRE_FLOP:
        betting_stage = BettingStagesEnum.FLOP
    elif betting_stage == BettingStagesEnum.FLOP:
        betting_stage = BettingStagesEnum.TURN
    elif betting_stage == BettingStagesEnum.TURN:
        betting_stage = BettingStagesEnum.RIVER
    elif betting_stage == BettingStagesEnum.RIVER:
        betting_stage = BettingStagesEnum.SHOWDOWN
    elif betting_stage == BettingStagesEnum.SHOWDOWN:
        betting_stage = BettingStagesEnum.PRE_FLOP
        
    return betting_stage
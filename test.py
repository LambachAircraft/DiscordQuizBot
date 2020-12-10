import discord
import time
from discord.ext.tasks import loop

client = discord.Client()

ch = ""

question_number = 1

quiz_started = False
registering = True
practice = False

quizzers = []
practice_team_answers = []

begin_time = time.perf_counter()
# check answer order questions 17,18,19
#                                                                              TEMPORARY!
#              1    2    3    4    5    6    7    8    9    10  11    12   13   14   15   16   17   18   19   20  21   22    23   24   25   26   27   28    #          V                             V    V
answer_key = ['A', 'A', 'C', 'D', 'C', 'D', 'A', 'C', 'A', 'B', 'C', 'C', 'A', 'B', 'C', 'A', 'A', 'C', 'B', 'C', 'B', 'B', 'B', 'D', 'A', 'D', 'A', 'C', 'A', 'A']
answer_time = [45, 45, 45, 45, 45, 45, 45, 45, 60, 45, 45, 45, 45, 60, 60, 45, 45, 60, 45, 30, 45, 45, 45, 30, 30, 30, 30, 60, 45, 30]
#                                                  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29  30
class Quizzer:
    def __init__(self, discord_user, team_name):
        self.discord_user = discord_user
        self.team_name = team_name
        self.answers = []

    def register_answer(self, answer):
        while question_number-1 > len(self.answers):
            self.answers.append(None)
        if question_number-1 == len(self.answers):
            self.answers.append(answer)
        else:
            self.answers[question_number-1] = answer

    def calc_score(self):
        score = 0
        for i in range(len(answer_key)):
            if i >= len(self.answers):
                break
            if self.answers[i] == answer_key[i]:
                score += 1
        return score

    def __str__(self):
        return self.team_name

def calc_percentage():
    correct_answers = 0
    number_of_answers = 0
    for quizzer in quizzers:
        number_of_answers += 1
        try:
            if quizzer.answers[question_number-1] == answer_key[question_number-1]:
                correct_answers += 1
        except:
            print("empty answer")
    if number_of_answers > 0:
        perc = round(correct_answers/number_of_answers * 100)
    else:
        perc = 0
    return perc

async def practice_question():
    global practice
    practice = True
    global begin_time
    begin_time = time.perf_counter()
    await ch.send(
        "Practice question is now open for answers, you have 45 seconds to answer.")

async def practice_question_closed():
    global practice
    practice = False
    await ch.send("Practice question closed! Received answers from following teams:")
    for team in practice_team_answers:
        await ch.send("-\t{}".format(team))

async def close_question():
    global quiz_started
    quiz_started = False
    await ch.send("Question {} CLOSED. Results: {}% answered correctly".format(question_number, calc_percentage()))

async def first_question():
    global quiz_started
    quiz_started = True

    global begin_time
    begin_time = time.perf_counter()
    await ch.send("Question {} is now open for answers, you have {} seconds to answer. Good luck!".format(question_number, answer_time[question_number-1]))


async def increase_question():
    global question_number
    question_number += 1
    print(ch)
    global quiz_started
    quiz_started = True

    global begin_time
    begin_time = time.perf_counter()
    await ch.send("Question {} open for answers, you have {} seconds to answer".format(question_number, answer_time[question_number-1]))

async def almost_closed():
    await ch.send("10 seconds left!")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    global ch
    ch = client.get_channel(775091942840205332)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.channel.DMChannel):
        pass
    else:
        return
    global registering
    if message.content.startswith(">register") and registering:
        team_name = message.content[10:]
        quizzers.append(Quizzer(message.author, team_name))
        print("{} has registered for team {}".format(message.author, team_name))
        await message.channel.send("You have been registered as the designated answerer for your team {}!".format(message.content[10:]))
        return

    if quiz_started or practice:
        if message.content.startswith('A') or message.content.startswith('B') or message.content.startswith('C') or message.content.startswith('D') or message.content.startswith('E') or message.content.startswith('F') or message.content.startswith('a') or message.content.startswith('b') or message.content.startswith('c') or message.content.startswith('d') or message.content.startswith('e') or message.content.startswith('f'):
            answer_letter = message.content[0]
            answer_letter = answer_letter.upper()
            await message.channel.send('You answered {} to question number {}'.format(answer_letter, question_number))
            for quizzer in quizzers:
                if quizzer.discord_user == message.author:
                    if quiz_started:
                        quizzer.register_answer(answer_letter)
                        print(
                            "{} answered {} for question {}".format(quizzer.team_name, answer_letter, question_number))
                    if practice:
                        if not(quizzer.team_name in practice_team_answers):
                            practice_team_answers.append(quizzer.team_name)
                        print(
                            "{} answered {} for practice question".format(quizzer.team_name, answer_letter))
                    return

    if message.content.startswith('>practice'):
        if message.author.name == 'mgos':
            await practice_question()
        else:
            await message.channel.send("Nice try ;)")

    if message.content.startswith('>start'):
        if message.author.name == 'mgos':
            await first_question()
        else:
            await message.channel.send("Nice try ;)")

    if message.content.startswith('>next'):
        if message.author.name == 'mgos':
            await increase_question()
        else:
            await message.channel.send("Nice try ;)")




    if message.content.startswith('>stop'):
        if message.author.name == 'mgos':
            for quizzer in quizzers:
                print("\n{} answers:".format(str(quizzer)))
                q_num = 1
                for answer in quizzer.answers:
                    print("Q{}:\t{}".format(q_num, answer))
                    q_num += 1
                print("==SCORE: {}==".format(quizzer.calc_score()))
            await client.close()

    if message.content.startswith('>finishreg'):
        if message.author.name == 'mgos':
            registering = False
            await ch.send("{} teams are registered, quiz will start in a few moments... Good luck!".format(len(quizzers)))


@loop(seconds=1)
async def timer_check():
    #await client.wait_until_ready()
    #print(time.perf_counter() - begin_time)
    if practice:
        timeout = 45
    else:
        timeout = answer_time[question_number-1]
    if (time.perf_counter() - begin_time > 1) and (quiz_started or practice):
        print(timeout-int(time.perf_counter() - begin_time))
    if(int(time.perf_counter() - begin_time) == timeout-10) and (quiz_started or practice):
        await almost_closed()
    if (time.perf_counter() - begin_time > timeout) and quiz_started:
        print("close question!")
        await close_question()
    if (time.perf_counter() - begin_time > timeout) and practice:
        print("close practice question!")

        await practice_question_closed()

timer_check.start()
client.run('NzQ2MDY0NjY2NjcyODg5OTQ3.Xz643Q.Mk7i1zIJCg4A4y_jusXrbozQEF0')
# IST356 Assignment 06 (assignment_06)

## Meta Section

### Prerequisites 

Before starting this assignment you must:

Install the assignment python requirements:

1. From VS Code, open a terminal: Menu => Terminal => New Terminal
2. In the terminal, type and enter: `pip install -r requirements.txt`

### Running Tests

There is some code and tests already working in this assignment. These are sanity checks to ensure VS Code is configured properly.

1. Open **Testing** in the activity bar: Menu => View => Testing
2. Open the **>** by clicking on it next to **assignment_06**. Keep clicking on **>** until you see **test_should_pass** in the **test_assignment.py**
4. Click the Play button `|>` next to **test_should_pass** to execute the test. 
5. A green check means the test code ran and the test has passed.
6. A red X means the test code ran but the test has failed. When a test fails you will be given an error message and stack trace with line numbers.


### Debugging

Odds are you will need to use some debugging strategies in this assignment. 

- To debug a test:
    - call the test function in the `if __name__ == '__main__':` block at the bottom of the test file.
    - then set a breakpoint in the test function and run the test as you would any other python program.
    - run the file with debugging: Menu => Run => Start Debugging

- To debug a streamlit, you can use the `st.write()` function to print out variables to the web page. You can also set breakpoints in the code and run the file with debugging: Menu => Run => Start Debugging


## Assignment: API's and Data Pipelines

In this assignment we will build a feature extraction data pipeline. The input will be a list of places and the output will be the conversations people are having about those places.

We will use the Google Places API to get the reviews of the places, the Azure Sentiment API to get the sentiment of the reviews, and the Azure Entity Extraction API to get the entities in the reviews so we know what the people are talking about. From this data we should be able to determine what people are speaking about specifically for each place and how they feel about it. For example: I like the food, but the customer service is poor. 

**NOTE:** We will analyze and visualize a larger dataset of this same datain a future assignment. For now we are just focused on building the data pipeline to prepare the data for future analysis.

### Introducing Multi-step Data Pipelines

One way to break up complex data pipelines is with a multi-step Extract-Transform-Load (ETL) approach. In this approach we complete mini ETL program where the output of one Python program forms the input of the next. This allows us to break up the problem into smaller, more manageable steps that are testable and easier to debug. It's also a way to cache API calls as as we write the output of each step of our data pipeline to a file. Since this assignment focuses on API's I thought it would be a good opportunity to introduce this concept!

While I'm simplifying the concept a bit for this assignment. This is so common with data pipelines, tools exists to make this easier such as [https://dagster.io/](https://dagster.io/) and [https://airflow.apache.org/](https://airflow.apache.org/). The AWS cloud has a platform called [Glue](https://aws.amazon.com/glue/) and [Step Functions](https://aws.amazon.com/step-functions/). 

The trick to creating a useful multi-step ETL is to:

1. keep the transformations in each step mangagable and easy to understand. 
2. output from any one step should be the input into the next step
3. break things up so expensive tasks like API calls and GPU usage from AI do not have to be repeated while building steps.
4. steps should be dependent ONLY on the output of previous steps, or extracts.

### Best practices for multi-step Pipelines

As a best-practice:

1. Each step is a python function
2. Function inputs are a data-like objects (Pandas Dataframe in our case) OR a filename (csv file in our case)
    1. when a filename is passed in we read the file as data-like object e.g. pd.read_csv(filename)
2. Function outputs should:
    1. Always cache the data-like to a file pd.to_csv() 
    2. and return the dataframe 

This way we can build the entire pipeline in memory or on disk.


## Working on this assignment

COMMIT YOUR CODE AFTER COMPLETION OF EACH PART 1 and 2. DO NOT PUSH, ONLY COMMIT.

### Part 0: Example of a multi-step ETL Pipeline

To help clarify this concept of a multi-step pipeline, I've included a simple example for you to explore. 

`example_etl.py`

This is a two-step pipeline. I suggest running the code and stepping through it in the debugger to see how it works.

This will provide some significant insight into how to build the multi-step ETL pipeline for this assignment.


### Part 1: First complete the code in `apicalls.py` 

Your first coding task is to complete all functions in `apicalls.py` and get the tests to pass under `test_apicalls.py`

You will need these functions to complete the multi-step ETL pipeline in the next part.

Start by setting your APIKEY to your CENT iSchool IoT Portal API key. [https://cent.ischool-iot.net](https://cent.ischool-iot.net)


**IMPORTANT:** Once your tests pass, run these tests anymore - you'll chew up your API quota!

### Part 2: Complete the multi-step ETL pipeline in `assignment_etl.py`

Inside this file there are 3 functions to implement:

- `reviews_step()`
- `sentiment_step()`
- `entity_extraction_step()`

Each function is a step in the multi-step ETL pipeline, and includes tests in `test_assignment_api.py` to help you verify your code is correct. This code looks for the output files and checks them. It does not call the API's or run your code!!!

AS YOU COMPLETE EACH FUNCTION, CALL THE FUNCTION UNDER `if __name__ == '__main__'` TO MAKE SURE IT EXECUTES. THE TESTS ONLY LOOK FOR THE OUTPUT FILES FROM THE PIPELINE RUNS. 

#### The multi-step ETL for this assignment

Here's the multi-step ETL for this assignment:

Steps: 

  1. place_ids --> reviews_step --> reviews (one row == user review of a place)
  2. reviews --> sentiment_step --> review_sentiment_by_sentence (one row == one sentence of text in a user's review of place)
  3. review_sentiment_by_sentence --> entity_extraction_step --> review_sentiment_entities_by_sentence (one row == one extracted entity from the sentence text of in a user's review of a place)

  Specifics for Each Step to help you write them:

    reviews_step:
        input: place_ids as a filename or a dataframe
        output: write CACHE_REVIEWS_FILE and return the dataframe
        Process: (A suggested approach)
            1. For each place in the input, call the google places API to get the place details and reviews. Make a Python list of dict where each dict is under the ['result'] key of the response from the API call. 
            2. Use json_normalize to Transform the json to be at the 'reviews' level, adding back the place_id, name from the parent level.
            3. Filter dataframe to these columns: place_id, name (of place), author_name, rating, text 

    sentiment_step:
        input: reviews from previous step as a filename or a dataframe
        output: write CACHE_SENTIMENT_FILE and return the dataframe
        Process: (A suggested approach)
            1. For each place in the input, call the azure sentiment API to get the sentiment of the text.
                Extract the results under ['results']['documents'][0]. This should be a dict.
                Add to the results the place_id and name of the place, author_name, and rating 
            2. Use json_normalize to Transform the json to be at the sentences level, adding back the place_id, name, author_name, and rating from the parent level.
            3. Rename the "text" column to "sentence_text" and the "sentiment" column to "sentence_sentiment"
            4. Filter to these columns: place_id, name, author_name, rating, sentence_text, sentence_sentiment, confidenceScores.positive,confidenceScores.neutral, confidenceScores.negative

    entity_extraction_step:
        input: review_sentiment_by_sentence from previous step as a filename or a dataframe
        output: write CACHE_ENTITIES_FILE and return the dataframe
        Process: (A suggested approach)
            1. For each place in the input, call the azure entity extraction API to get the entities in the text.
                Extract the results under ['results']['documents'][0]
                Add to the results all the columns in the input 
            2. Use json_normalize to Transform the json to be at the entities level, adding back all the columns in the input dataframe as the parent level.
            3. Rename these columns: the "text" column to "entity_text" and the "category" column to "entity_category", the "subCategory" column to "entity_subCategory", and the "confidenceScore" column to "confidenceScores.entity"
            4. Filter to these columns: place_id, name, author_name, rating, sentence_text, sentence_sentiment, confidenceScores.positive,confidenceScores.neutral, confidenceScores.negative, entity_text, entity_category, entity_subCategory, confidenceScores.entity


#### Sanity Checks

    - place_ids.csv has just 2 places, thus 2 rows
    - reviews.csv has 10 reviews (5 for each place), thus 10 rows
    - At the time of writing this assignment there were 88 sentences total among the 10 reviews.
    - At the time of writing this assignment there were 123 entities extracted among the 88 sentences.

    Outputs from the solution runs are in the `code/colutions/cache` folder.


#### DON't FORGET!

Your actual pipeline should be under the `if __name__ == '__main__':` block in `assignment_etl.py` so it runs when you execute the file.

The tests will not pass unless you run the pipeline!

## Turning it in 

### Commit Requirements

If you followed directions, you should have your 2 git commits minimum. Its okay to have more, but you should have at least 2.


- Make sure tests pass and code works as expected
- Write your reflection in `reflection.md`
- Commit your changes: VS Code -> menu -> View -> Source Control -> Enter Commit message -> Click "Commit"
- Push your changes: VS Code -> menu -> View -> Source Control -> Click "Sync Changes"

## Grading 

🤖 Beep, Boop. This assignment is bot-graded! When you push your code to GitHub, my graderbot is notified there is something to grade. The bot then takes the following actions:

1. Your assignment repository is cloned from Github
2. The bot checks your code and commits according to guidelines outlined in `assignment-criteria.json` (it runs tests, checking code correctness, etc.)
3. The bot reads your `reflection.md` and provides areas for improvement (based on the instructions in the file).
4. A grade is assigned by the bot. Feedback is generated including justification for the grade given.
5. The grade and feedback are posted to Blackboard.

You are welcome to review the bot's feedback and improve your submission as often as you like.

**NOTE: ** Consider this an experiment in the future of education. The graderbot is an AI teaching assistant. Like a human grader, it will make mistakes. Please feel free to question the bots' feedback! Do not feel as if you should gamify the bot. Talk to me! Like a person, we must teach it how to do its job effectively. 

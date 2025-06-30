## Introduction
This project is a web app for tracking the performance of stock portfolios v. market indexes. It has been developed via agentic coding. This file sets the context for AI agents to work. 

## Preparation for the AI agent
1. The project has a docs folder with requirements, high-level design, component design, UI wire frames and more. Please reviews those docs prior to starting work. 
2. We're using Github for source control. We have three branches, main, devQ and devR. 
3. The three branches are deployed to Heroku as follows.
    1. Main is deployed here: https://mystocktrackerapp-prod-32618c8b4af1.herokuapp.com/
    and referred to as Prod. 
    2. devQ is deployed here: https://mystocktrackerapp-devq-6cb9ce7e7076.herokuapp.com/ and referred to as devQ. 
    3. devR is deployed here: https://mystocktrackerapp-devr-607807562777.herokuapp.com/dashboard and referred to as devR.
4. There is a file at /Users/craigrow/q/src/AmazonBuilderGenAIPowerUsersQContext/scripts/code-assist.script.md with further instructions for AI agents. 
5. Before starting any coding, please become familiar with all the documents mentioned above and confirm any details necessary.

## Code Quality
1. We have an extensive test suite. Promotion from dev branches to main may not happen until.
    1. All changes from main have been pulled down to dev, and
    2. All tests are passing 100%, and
    3. UAT has been completed and passed.
2. We have real using who have dependencies on Main. No breaking changes are acceptable in Main. 


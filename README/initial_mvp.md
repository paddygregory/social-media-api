# WHAT IS the AI social media content generator API?

I am building a content generating API powered by OpenAI's API keys that takes a prompt and returns content generated in an instagram, twitter and linkedin format.
The application will take length and tone specifications, and aim to be implementable into different styles for each platform, such as a Twitter 'thread,' or an extended Linkedin 'blog.'
The content generator will be free to use, and eventually will be built on FastAPI, a PostGreSQL database and async operating using celery, redis and FastAPI's async tools.

What will the ENDPOINTS be for the social media content generator API?

the AI content generator will have three endpoints: 

1. /generate POST

   The generate post will take a user input (moderated to avoid token abuse) and return an OpenAI generated response, using the following *rough* JSON sketch:
{
   "PROMPT":
   "User input here"
             }
   {
   "RESPONSE": "Twitter":
   
                "Instagram":
   
                "Linkedin":

                "Engagement optimisation":
                }
This JSON sketch will only be applied after the below tone/length customisation is given.

2. /templates GET:

   The templates post will allow a user to select a tone (professional, witty, humorous etc) and length (short, medium, long) for their content generation. The following *rough* JSON sketch applies:

    {"PROMPT:
   "select a tone and length
               *dropdown of tone and length in frontend*
              }

   {
   "RESPONSE": "Twitter":
   
               "Instagram":
   
               "Linkedin":

               "Engagement Optimisation":
   }

   3. /health GET:

   the /health GET will only be for developer assurance, serving as an initial endpoint and easy access spot for UptimeRobot pinging, FastAPI status etc.

# Import necessary modules
from django.shortcuts import render
from django.http import HttpResponse
from naukri_app.modules.scraper import Naukri_Scraper
import logging

# Get an instance of a logger
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging_format = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('naukri_app_log.log')
file_handler.setFormatter(logging_format)
logger.addHandler(file_handler)

def home(request):
    # Render the home page
    return render(request,"index.html")

def get_jobs(request):
    try:
        # Check if the request method is POST
        if request.method == "POST":
            # Get the data from the POST request
            data = request.POST
            # Get the job designation from the data
            designation = data.get("designation")

            # Create a Naukri_Scraper object with the given designation
            jobs = Naukri_Scraper(designation)
            # Scrape the jobs for the given designation
            job_dict = jobs.scrap_jobs()
            # Create a context dictionary to pass to the template
            context = {"jobs":job_dict}
    
            # Render the scraped_data.html template with the context
            return render(request,"scraped_data.html",context)
        logger.info("Done!")
    except Exception as e:
        # Log the exception
        logger.error(f'Error occurred: {e}')
        # Print the exception (You might want to remove this in a production environment)
        return HttpResponse("An error occurred. Please try again.")  # Return an error message

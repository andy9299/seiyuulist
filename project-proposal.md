# Capstone-Project-1
### 1. What goal will your website be designed to achieve?  
\- Site for people to view anime information and information about voice actors.  
\- Functionality to favorite artists/anime (accounts needed)  
\- Functionality to filter anime based on 1 to x amount of voice actors  
\- Homepage displayed with voice actors from newest animes  
\- User page displays top 10 favorites   
### 2. What kind of users will visit your site? In other words, what is the demographic of
your users?  
\- People who are looking for anime based on voice actors
### 3. What data do you plan on using? You may have not picked your actual API yet,
which is fine, just outline what kind of data you would like it to contain.  
\- https://docs.api.jikan.moe/
### 4. In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:  
* What does your database schema look like?  
\- Accounts (primary key: username; password)  
\- Favorite Voice actors (primary key: username & voice actor)  
\- Favorite  Animes (primary key: username & anime name)  
* What kinds of issues might you run into with your API?  
\- api could go down  
* Is there any sensitive information you need to secure?  
\- passwords  
* What functionality will your app include?  
\-  above  
* What will the user flow look like?  
\-  homepage (able to view voice actors from recent anime) -> login/register in navbar -> search animes/voice actors -> favorite -> view suggestions  
* What features make your site more than CRUD? Do you have any stretch goals?  
\- follows / follows activity page
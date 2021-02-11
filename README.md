# ModelTrain

Check it out here! [Deployed Site](https://model-train.herokuapp.com/)

> ## Description
>
> ModelTrain is a machine learning platform built with **Python Flask** for data analysts to create and store projects in a **Postgres** database. ModelTrain makes use of **Redis Queue** for job processing and features a frontend built with **HTML5, CSS3, JavaScript,** and **Bootstrap5**.

---

## Technologies

### Python

- Pandas: Dataframe object was used to store and transform user supplied data
- Gensim and NLTK: Preprocessing data upon which the Latent Dirichlet Allocation model was applied. Gensim's LDA model was used for topic modeling
- Scikit-Learn: Linear Regression model used

### Flask

- Sever and communication of client requests and data storage to Postgres database
- Verification of security of user-uploaded files
- Execution of ML scripts
- Restrictded access routes

### Postgres

- Database

### Redis Queue

- Background execution of ML project creation scripts while the application to maintain normal request and response thresholds

### Bootstrap, HTML, CSS, JavaScipt

- Responsive design
- Easily navigatable home dashboard
- Logical flow of ML project creation
- User-friendly interactions

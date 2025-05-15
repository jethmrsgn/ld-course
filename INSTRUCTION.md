# Instruction

**Instruction on how to run this repository in your local machine.**

1. Clone this repository to your local machine
<pre>git clone https://github.com/jethmrsgn/ld-course.git</pre>

2. Go to the directory of the cloned repository.
<pre>cd path/to/cloned_repository</pre>

3. In your git terminal execute this code to create and run the docker image.
<pre>docker build -t course-app .
docker run -p 8002:8002 course-app</pre>
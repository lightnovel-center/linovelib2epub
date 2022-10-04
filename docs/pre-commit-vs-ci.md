## pre-commit与ci的区别

第一，任务轻重不同。
- pre-commit一般是一些轻量的任务,例如isort flake8 black
- 而ci除了上述的任务，也可以执行一些厚重的task，例如pytest、pytest-cov、publish。
  因为一次commit必然不能过重，试想一次commit需要30分钟的前置hooks任务，那么每次commit将变得很重，不利于开发commit。所以，pre-commit的任务一般为代码检测。

第二，阶段不同。
- pre-commit是在本地开发时，git commit之前执行。这可以认为是提前预防。
- ci是本地开发的代码push到远程代码库之后执行。这可以认为是事后检测。
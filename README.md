# TigerGraphHackathon
Tiger Graph Hackathon

---
## Repository Setup
1. Fork the main repository
2. Clone your fork of the repository and `cd` into the directory

```
$ git clone https://github.com/yourUsername/TigerGraphHackathon.git
$ cd TigerGraphHackathon
```
3. Set the main repository as the upstream
```
$ git remote add upstream https://github.com/rviccina/TigerGraphHackathon.git
```
- For a sanity check, run this command `$ git remote -v` and you'll see something similar to this:
```
$ git remote -v
origin	https://github.com/yourUsername/TigerGraphHackathon.git (fetch)
origin	https://github.com/yourUsername/TigerGraphHackathon.git (push)
upstream	https://github.com/rviccina/TigerGraphHackathon.git (fetch)
upstream	https://github.com/rviccina/TigerGraphHackathon.git (push)
```
---
## Flow for submitting a Pull Request
1. Create a feature branch off of the master branch

- To check which branch you're on, use `$ git status`
```
$ git checkout -b name-of-feature-branch
```
2. Add, commit, and push your changes:
```
$ git commit -a -m "Added csv file"
$ git push origin name-of-feature-branch
```
3. Once you push the changes to your repo, the **Compare & pull request** button will appear in GitHub. It will look similar to the following:

baseRepository: **rviccina/repo** base: **master** <- headRepository: **yourUsername/TigerGraphHackathon** compare: **name-of-feature-branch**


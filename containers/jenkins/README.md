# Jenkins practice lab

One Jenkins container on INTELi7, for learning. It is not connected to any other
host and deploys nothing. Run the commands from this directory.

## Start

```powershell
docker compose up -d
```

Show the one-time password for the setup wizard:

```powershell
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open <http://localhost:8080>, enter that password, choose **Install suggested
plugins** and create your admin user.

## Exercise 1: hello world

1. Select **New Item**, name it `hello`, choose **Freestyle project** and
   confirm.
2. Under **Build Steps**, add **Execute shell** with:

   ```sh
   echo "Hello from Jenkins"
   whoami
   pwd
   ```

3. Save, then select **Build Now**.
4. Open the build in **Build History** and read its **Console Output**.

The commands run inside the Linux container, not in Windows.

Jenkins warns about running builds on the built-in node. That is acceptable for
this practice with your own commands. In a real setup, builds run on separate
agents, because a job on the built-in node can access Jenkins' own files.

## Exercise 2: first pipeline

1. Select **New Item**, name it `hello-pipeline`, choose **Pipeline** and
   confirm.
2. Under **Pipeline**, keep **Pipeline script** and paste the contents of
   [`Jenkinsfile`](Jenkinsfile).
3. Select **Build Now** and read the **Console Output**.
4. In the `Test` stage, change `grep hello` to `grep goodbye` and build again.
   `grep` returns a non-zero exit code, so `Test` fails and `Report` is skipped.
   Compare which `post` messages appear.
5. Restore `grep hello`.

## Exercise 3: pipeline from Git

Jenkins reads the `Jenkinsfile` from GitHub, so it must be committed and pushed.

1. Open `hello-pipeline` and select **Configure**.
2. Under **Pipeline**, change the definition to **Pipeline script from SCM**:
   - SCM: **Git**
   - Repository URL: `https://github.com/rmadc/nixos-config.git`
   - Branch Specifier: `*/main`
   - Script Path: `containers/jenkins/Jenkinsfile`
3. Save and select **Build Now**. No credentials are needed while the
   repository is public.

The console shows Jenkins fetching the repository and the commit it checked out.

To see the effect of a change, edit the `Jenkinsfile`, commit, push and build
again. An edit that is not pushed has no effect on the build. This lab has no
automatic trigger yet, so start each build with **Build Now**.

## Stop and resume

```powershell
docker compose stop
```

```powershell
docker compose start
```

The container does not start by itself after a restart. `docker compose down`
removes the container but keeps the `jenkins-home` volume. Adding `-v` also
deletes the volume, with all jobs and users.

# Jenkins lab

A Jenkins controller and one build agent on INTELi7. It checks pull requests and
`main` of this repository and reports the result to GitHub. It deploys nothing.

| File | Contents |
| --- | --- |
| `compose.yaml` | Controller and agent containers |
| `agent/Dockerfile` | Build tools available on the agent (ShellCheck, Ruff) |
| `Jenkinsfile` | The checks that run |
| `.env.example` | Template for the untracked `.env` file |
| [`ruff.toml`](../../ruff.toml) | Python lint rules, in the repository root |
| [`CONCEPTS.md`](CONCEPTS.md) | Reminder of the Jenkins concepts practised here |

Run the commands below from this directory.

## What is not in Git

Only the files above are in Git. Jobs, plugins, users and credentials are set up
in the web interface and stored in the `jenkins-home` volume. The agent secret
is in `.env`. Deleting the volume means repeating the setup below.

## Set up from scratch

### 1. Controller

```powershell
docker compose up -d jenkins
```

Show the one-time password for the setup wizard:

```powershell
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open <http://localhost:8080>, enter that password, choose **Install suggested
plugins** and create your admin user.

### 2. Agent

1. Under **Manage Jenkins** > **Nodes**, select **New Node**. Name it
   `practice-agent`, choose **Permanent Agent** and set:
   - Remote root directory: `/home/jenkins/agent`
   - Labels: `practice`
   - Launch method: **Launch agent by connecting it to the controller**
   - **Use WebSocket**, if the option is shown
2. Copy `.env.example` to `.env` and replace `replace-me` with the secret shown
   on the node's page. Do not commit it: the repository is public.
3. Build and start the agent:

   ```powershell
   docker compose up -d --build agent
   ```

4. Check that the node is online. Then set the number of executors of the
   built-in node to `0`, so that builds cannot run on the controller.

### 3. GitHub token

On GitHub, create a fine-grained personal access token limited to this
repository, with an expiry date and these repository permissions:

| Permission | Access |
| --- | --- |
| Contents | Read-only |
| Pull requests | Read-only |
| Commit statuses | Read and write |

In Jenkins, under **Manage Jenkins** > **Credentials** > **System** > **Global**,
add it as **Username with password**: username `rmadc`, the token as the
password and ID `github-token`.

When the token expires, create or regenerate it and update the password of that
credential. A `403` when updating a commit status, shown in the build log, means
the token lacks permission.

### 4. Job

Create a **Multibranch Pipeline** named `hello-github`:

- Branch source: **GitHub**, credentials `github-token`, repository
  `https://github.com/rmadc/nixos-config.git`
- Under **Behaviours**, delete **Discover pull requests from forks**. Anyone can
  fork a public repository, and their code must not run on this machine.
- Script path: `containers/jenkins/Jenkinsfile`
- Scan triggers: **Periodically if not otherwise run**, 2 minutes

Jenkins polls because GitHub cannot reach `localhost` with a webhook.

### 5. Protect `main`

On GitHub, under **Settings** > **Rules** > **Rulesets**, create a branch ruleset
for the default branch:

- **Require a pull request before merging**, with 0 required approvals
- **Require status checks to pass**, with the check
  `continuous-integration/jenkins/pr-head`

Merging then needs this lab to be running. If it cannot run, the ruleset can be
disabled temporarily.

## Make a change

1. Switch to `main` and pull.
2. Create a branch, make the change, commit and publish the branch.
3. Open a pull request. Jenkins finds it at the next scan.
4. Merge when the check has passed. The **Details** link of the check opens the
   build, and only works on INTELi7.
5. Delete the branch, then switch to `main` and pull.

The check tests the branch as it is, not combined with newer commits on `main`.
If `main` has changed, update the branch before merging.

A passing check covers only what the `Jenkinsfile` runs. It does not validate
the Compose files or the NixOS configurations. Review changes to the
`Jenkinsfile` carefully, because a pull request can change its own checks.

## Add a tool to the agent

Add it to `agent/Dockerfile`, then rebuild while no build is running:

```powershell
docker compose up -d --build agent
```

Do this before pushing a `Jenkinsfile` that needs the tool. Package versions are
not pinned, and a cached build step does not fetch newer versions.

## Operate

```powershell
docker compose stop
```

```powershell
docker compose start
```

The containers do not start by themselves after a restart. `docker compose down`
removes the containers but keeps the `jenkins-home` volume. Adding `-v` also
deletes the volume, with all jobs, users and credentials.

Before applying a change to `compose.yaml`, preview which containers it affects:

```powershell
docker compose up -d --dry-run
```

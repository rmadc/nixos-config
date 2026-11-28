# Jenkins concepts

A reminder of what was practised in this lab. The snippets are fragments: the
[`Jenkinsfile`](Jenkinsfile) holds the real checks, and the
[README](README.md) explains the setup.

## Pipeline

A pipeline is stages, run in order. It lives in a `Jenkinsfile` in Git, so
changes to it are reviewed like any other code.

```groovy
pipeline {
  agent { label 'practice' }
  stages {
    stage('Check') {
      steps {
        sh './check.sh'
      }
    }
  }
}
```

A step fails when its command exits with a non-zero code. The stages after it
are skipped.

## Controller and agents

The controller manages jobs and credentials. Agents run builds.

- `agent { label 'practice' }` selects any online agent with that label. A label
  is not the node's name.
- A build can only use tools installed on its agent. Defining them in a
  `Dockerfile` keeps the setup in Git.
- Each job has a workspace on the agent. Later builds can overwrite its files.

## Triggers

| Trigger | How a build starts |
| --- | --- |
| **Build Now** | By hand |
| Poll SCM | Jenkins checks one job's repository on a schedule |
| Multibranch scan | Jenkins looks for new branches, pull requests and commits |
| Webhook | GitHub notifies Jenkins; it must be able to reach Jenkins |

Polling in a single pipeline job, set in the web interface or the
`Jenkinsfile`:

```groovy
triggers {
  pollSCM('H/2 * * * *')
}
```

A pipeline job reading from Git has a **Branch Specifier**. It defaults to
`*/master`; this repository uses `main`.

## Multibranch pipelines and pull requests

A multibranch job creates one job for each branch and pull request that has a
`Jenkinsfile`. Each has its own history and build numbers. With the setting used
here, a branch with an open pull request appears only as the pull request.

Jenkins sends each result to GitHub as a commit status. A GitHub ruleset can
require that status before merging. A passing check covers only what the
pipeline ran.

## Parallel stages

Stages inside `parallel` run at the same time. The following stage waits for all
of them. A stage has either `steps` or `parallel`, not both.

```groovy
stage('Checks') {
  parallel {
    stage('Lint') {
      steps { sh './lint.sh' }
    }
    stage('Test') {
      steps { sh './test.sh' }
    }
  }
}
```

By default, one failing branch does not stop the others, so one build reports
all their problems. With `failFast true`, the first failure aborts the rest.

With the agent declared for the whole pipeline, as here, the branches share one
workspace. Do not let them write the same files.

## Running a stage only on some branches

`when` goes inside the stage. `branch` works in multibranch pipelines.

```groovy
stage('Publish') {
  when { branch 'main' }
  steps {
    sh './publish.sh'
  }
}
```

A skipped stage does not fail the build. Typical use: check every change, and
publish or deploy only from `main`.

## Post actions

`post` runs after the stages, at pipeline or stage level.

```groovy
post {
  success { echo 'Passed' }
  unstable { echo 'Some tests failed' }
  failure { echo 'Failed' }
  aborted { echo 'Aborted' }
  always { echo 'Runs in every case' }
}
```

## Parameters

Parameters are values given when a build starts. They are also available to the
shell as environment variables.

```groovy
parameters {
  string(name: 'GREETING', defaultValue: 'hello', description: 'Text to write')
}
```

```groovy
sh 'echo "$GREETING"'
```

Use single quotes around the command, so that the shell reads the variable and
Groovy does not insert the input into the command.

Jenkins learns about parameters by running the `Jenkinsfile`. In the lab, the
first build after adding them got an empty value, and **Build with Parameters**
appeared only afterwards.

## Manual approval

```groovy
stage('Approve') {
  steps {
    input message: 'Deploy?', ok: 'Deploy'
  }
}
```

The build waits. Aborting it skips the following stages and ends as `ABORTED`.

## Credentials

Store the secret in Jenkins and refer to it by ID. Only the ID goes into Git.

```groovy
environment {
  TOKEN = credentials('example-token')
}
```

Jenkins masks the value in the log, but this is not a security boundary: whoever
can change the pipeline can extract the secret. Review changes to pipelines that
use credentials.

## Artifacts

An artifact is a file kept with a particular build, such as a package or a
report.

```groovy
archiveArtifacts artifacts: 'dist/*', fingerprint: true
```

`fingerprint` records a checksum, so that Jenkins can tell which builds
produced or used the same file.

- The workspace can still hold files from an earlier build. Empty the output
  folder before filling it, or old files get archived too.
- A package should say where it came from, for example with the commit ID and
  file hashes.
- `git archive` packages files as they are in a commit, so untracked files such
  as `.env` are left out.

## Test reports

Test tools can write JUnit XML reports. Jenkins then shows which tests failed
and why.

```groovy
post {
  always {
    junit 'results.xml'
  }
}
```

| Result | Typical meaning |
| --- | --- |
| `SUCCESS` | Everything passed |
| `UNSTABLE` | The pipeline ran, but some tests failed; later stages still run |
| `FAILURE` | A step failed; later stages are skipped |
| `ABORTED` | The build was stopped |

For the report to mark a build `UNSTABLE`, the test command must not already
have failed the step. Many test tools exit with a non-zero code when a test
fails, which gives `FAILURE` unless the pipeline handles it.

pytest exits with `1` when tests fail and with other non-zero codes when it
cannot run them properly. This accepts only `1`, and leaves the verdict to the
report:

```groovy
sh '''
  rm -f results.xml
  pytest --junitxml=results.xml path/to/tests || [ "$?" -eq 1 ]
'''
```

## Reviewing a pull request

- Check the result for the latest commit, and read the changes.
- If a build fails and then passes with the same code, find out why.
- Check changes to the `Jenkinsfile` carefully: a pull request can change its
  own checks.
- Remember what was not tested, such as stages that run only on `main`.

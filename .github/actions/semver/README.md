# SemVer docker action

Calculates the next SemVer tag based on the latest tag and the commit messages since then.

## Inputs

## Outputs

### `next_tag`

Next SemVer tag.

### `changelog_delta`

Every commit message since the last tag.

## Example usage

```yaml
      - name: Semver
        uses: ./.github/actions/semver
        id: semver
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Outputs can be accessed like this:

```yaml
      - name: Print next tag
        run: echo ${{ steps.semver.outputs.next_tag }}
```
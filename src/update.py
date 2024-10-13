from pathlib import Path
import urllib.request
import json

projects_dir = Path(__file__).parent


def project_list():
    return [
        p for p in projects_dir.iterdir() if p.is_dir() and (p / "build.py").exists()
    ]


def get_latest_version(upstream_url):
    repo, name = upstream_url.split("/")[-2:]
    with urllib.request.urlopen(
        f"https://api.github.com/repos/{repo}/{name}/releases/latest"
    ) as response:
        data = response.read().decode("utf-8")
        return json.loads(data)["tag_name"].lstrip("v")


def main():
    for project in project_list():
        build_file = project / "build.py"
        lines = build_file.read_text().splitlines()

        try:
            upstream_url = (
                [line for line in lines if "UPSTREAM_REPO" in line][0]
                .split("=")[1]
                .strip()
            )
            upstream_url = upstream_url[1:-1]  # remove quotes
            version = (
                [line for line in lines if "VERSION" in line][0].split("=")[1].strip()
            )
            version = version[1:-1]  # remove quotes
        except IndexError:
            print(f"Skipping {project.name}")
            continue

        latest_tag = get_latest_version(upstream_url)

        if latest_tag == version:
            print(f"{project.name} is already up to date")
            continue

        new_content = build_file.read_text().replace(version, latest_tag)
        build_file.write_text(new_content)
        print(f"{project.name} {version} -> {latest_tag}")


if __name__ == "__main__":
    main()

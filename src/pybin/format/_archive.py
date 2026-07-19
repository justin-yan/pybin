from pathlib import PurePosixPath


def select_archive_member(members: list[PurePosixPath], extract_spec: str) -> PurePosixPath:
    """
    Deciding which specific file to extract from an archive as the binary of interest is somewhat finicky.

    We could require that every single project needs to specify an exact pathspec to extract, which would be
      easy to implement but would add more onboarding friction.  Until it gets overly complicated, we're going to stick
      to this implementation, which gets an "extract_spec", which essentially defines which filename we want to pull.

    There are a few different cases that need to be handled:

    - Archive is a folder, holds binary at root of folder.
    - Archive is a folder, holds binary in a nested folder.
    - Archive is a single file, binary has full target name, not compact binary name
    """
    # Identify all files that match the extraction spec.  Windows .exe suffixes are added by whoever is creating the extract spec.
    matches = [member for member in members if member.name == extract_spec]

    # There are cases where the archive simply contains the binary, and it is named something weird.
    if not matches and len(members) == 1:
        matches = members

    # In cases where there is more than one match, we take the first match that sits in a `bin` directory, otherwise
    #   we take the head of the list (which would generally be the only match)
    return next((member for member in matches if member.parent.name == "bin"), matches[0])

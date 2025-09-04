import glob
import re
import os


class JMakeParser:
    def __init__(self, path):
        self.path = path
        self.project_name = None
        self.language = None
        self.targets = {}

    def parse(self):
        print(f"Opening file: {self.path}")
        print(f"File exists? {os.path.isfile(self.path)}")

        with open(self.path, "r") as f:
            lines = f.readlines()

        print(f"Number of lines read: {len(lines)}")
        for line in lines:
            line = line.strip()
            print(f"Line content: '{line}'")
            print(f"Parsing line: {line}")  # Debug print

            if line.startswith("project("):
                self.project_name = self._extract_arg(line)
            elif line.startswith("language("):
                self.language = self._extract_args(line)
            elif line.startswith("add_library("):
                name, sources = self._extract_name_and_sources(line)
                self.targets[name] = {"type": "library", "sources": sources, "deps": []}
            elif line.startswith("add_executable("):
                name, sources = self._extract_name_and_sources(line)
                self.targets[name] = {"type": "executable", "sources": sources, "deps": []}
            elif line.startswith("target_link_libraries("):
                target, deps = self._extract_target_and_deps(line)
                if target in self.targets:
                    self.targets[target]["deps"].extend(deps)

        print(f"Project: {self.project_name}")
        print(f"Language: {self.language}")
        print(f"Targets: {self.targets}")

    def _extract_arg(self, line):
        # Extract one argument inside parentheses
        match = re.match(r'\w+\((.+)\)', line)
        if match:
            return match.group(1).strip()
        return None

    def _extract_args(self, line):
        # Extract multiple args inside parentheses
        match = re.match(r'\w+\((.+)\)', line)
        if match:
            return match.group(1).strip().split()
        return []

    def _extract_name_and_sources(self, line):
        # Format: add_library(name sources...)
        match = re.match(r'\w+\((\w+)\s+(.+)\)', line)
        if match:
            name = match.group(1)
            # Expand glob patterns
            sources_glob = match.group(2).split()
            sources = []
            for pattern in sources_glob:
                files = glob.glob(pattern)
                if not files:
                    print(f"Warning: No files found matching pattern '{pattern}'")
                sources.extend(files)
            return name, sources
        return None, []

    def _extract_target_and_deps(self, line):
        # Format: target_link_libraries(target PRIVATE dep1 dep2 ...)
        match = re.match(r'\w+\((\w+)\s+PRIVATE\s+(.+)\)', line)
        if match:
            target = match.group(1)
            deps = match.group(2).split()
            return target, deps
        return None, []

    def generate_makefile(self, output_path):
        if not self.project_name:
            self.project_name = "UnnamedProject"

        with open(output_path, "w") as f:
            f.write(f"# Auto-generated Makefile for {self.project_name}\n")
            f.write("JAVAC=javac\n")
            f.write("JAVA=java\n")
            f.write("JFLAGS=\n\n")

            # Build list of executables for the 'all' target
            executables = [name for name, t in self.targets.items() if t["type"] == "executable"]
            if executables:
                f.write("all: " + " ".join(executables) + "\n\n")
            else:
                f.write("all:\n\n")

            # Write targets for executables and libraries
            for name, t in self.targets.items():
                # Build .class files list from source files
                class_files = [src.replace(".java", ".class") for src in t["sources"]]

                # Collect dependencies' class files (for linked libraries)
                deps_class_files = []
                for dep in t.get("deps", []):
                    if dep in self.targets:
                        dep_classes = [s.replace(".java", ".class") for s in self.targets[dep]["sources"]]
                        deps_class_files.extend(dep_classes)

                # Target depends on its .class files + deps' .class files
                all_deps = class_files + deps_class_files
                f.write(f"{name}: {' '.join(all_deps)}\n")
                # You can put a dummy command here or leave empty because actual compilation is handled by pattern rule
                f.write("\n")

            # Pattern rule: compile any .java to .class
            f.write("%.class: %.java\n")
            f.write("\t$(JAVAC) -cp src $(JFLAGS) $<\n\n")


            # Clean rule
            f.write("clean:\n")
            f.write("\trm -f **/*.class *.class\n")


if __name__ == "__main__":
    parser = JMakeParser("JMakeLists.txt")
    parser.parse()
    parser.generate_makefile("Makefile")
    print("Makefile generated successfully!")

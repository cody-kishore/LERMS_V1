
**LERMS (Local Resource Management System)** is a decentralized, offline educational application designed to bridge the digital divide in low-connectivity or high-density campus environments. The core innovation of LERMS lies in its ability to transform a standard smartphone or computer into a fully functional local server. By broadcasting a localized "Intranet" via a mobile hotspot, it allows surrounding users to download educational materials and execute code without consuming a single byte of cellular data.

The project won the *"Best Project Award"* (Outstanding Project of the Department) at the Science Day Expo (SAHAS26). It was built to solve practical infrastructure constraints: the inability to seamlessly distribute study files on weak campus networks and a lack of accessible physical computer laboratory space.

LERMS was engineered and demonstrated live under constraint environments using nothing but a personal mobile device framework. The implementation successfully outperformed enterprise presentation arrays, validating that optimized backend software architectures can efficiently bypass hardware limitations to solve immediate structural challenges.

---

### Core Architecture & Technical Stack

The system is engineered as a lightweight, cross-platform architecture that operates entirely client-side without relying on external cloud APIs.

* **Backend & Server Control:** Written in Python 3, leveraging standard libraries such as `http.server` and `socketserver`. It utilizes a multi-threaded daemon (`threading.Thread`) to keep the networking socket open in the background without freezing the host application.
* **Mobile Interface:** Built using **Kivy** and **KivyMD** (Material Design components for Kivy). This provides an adaptive dark-mode dashboard on Android to display local IP configurations, client logs, and a master toggle switch for host server execution.
* **Database Layer:** Operates directly on the native file system via a dedicated workspace directory named `Classroom_Sync`.
* **Frontend UI:** Built using standard responsive HTML5, CSS3, and vanilla JavaScript. The user interface serves a clean, blue-themed card layout for resource management and a dedicated dark-mode environment for the development workspace.

---

### Key Features & Operational Flow

#### 1. Automated Initialization & Deployment

When the host launches LERMS, the backend initializes an automated environment check (`ensure_base_path`). It programmatically scans the device to confirm whether the storage directory `Classroom_Sync` exists. If it is missing, the engine creates it and extracts embedded core assets (`template.html` and `compiler.html`) from its internal bundle directly into local storage. This makes the system plug-and-play, eliminating manual folder creation.
 
#### 2. System Flow
[Client Peer Device] ---> Requests Resource (Wi-Fi Hotspot) ---> [Gateway IP:8000] ---> [Custom Python Handler Engine] ---> [Local Filesystem / exec() Evaluator]


 53- **Backend & System Architecture:** Python 3 (`http.server`, `socketserver`, `threading`)
- **Controller Interface:** Kivy / KivyMD (Fully reactive application engine)
- **Frontend Presentation Layer:** Clean, responsive HTML5, CSS3, vanilla JavaScript (Asynchronous `Fetch` API mapping)
- **Deployment Platform:** Android SDK/NDK via Buildozer compilation toolchain

#### 3. Dynamic HTML Library Generation

When the host activates "Host Mode," the application triggers a compilation function (`build_library`):

* The script reads the template structure and runs a file-system scan to filter all files ending in a `.pdf` extension.
* It dynamically maps each PDF's file name into a responsive HTML layout component.
* Every mapped resource automatically generates standalone action buttons for inline viewing (`target="_blank"`) and direct physical download (`download`).
* The engine updates the directory tree safely by writing to a temporary file (`index.html.tmp`) and performing an atomic swap (`os.replace`) to ensure the server never serves a corrupted, zero-byte file if a system crash occurs mid-write.

#### 4. Isolated Offline Python Compiler

To substitute for a physical computer laboratory, LERMS includes a fully functional, browser-based coding environment.

* Connecting clients navigate to the internal compiler dashboard, write Python code inside a structural text interface, and hit a "Run" parameter.
* The client frontend marshals the raw string text and transmits it via an asynchronous JavaScript `POST` request to a custom network gateway (`/run_python`).
* The custom backend server intercepts the network payload, isolates the text block, and passes it to an internal execution engine using Python’s native `exec()` scope.
* To capture the code's output without printing it to the host terminal, LERMS dynamically wraps the system pipeline using `io.StringIO()` and `redirect_stdout`. The captured console output is caught, structured cleanly, and passed back across the network to the client browser. If the code crashes, custom exception filters catch the trace on line boundaries and send the exact error back to the student.

---

### Networking Architecture

The network logic relies on a standard Local Area Network (LAN) star topology created by the host device's Wi-Fi hotspot router module.

Because mobile operating systems route network adapters uniquely, the backend dynamically resolves the host interface's relative broadcast address through a raw socket query (`getsockname`) bound to an ephemeral outward network target.

By binding the network handler socket to an inclusive address string (`""`), the server listens uniformly across all active network boundaries (cellular adapters, Wi-Fi paths, and hotspot rings) on Port `8000`. Peers simply connect to the local hotspot infrastructure, open any standard browser, and input the target gateway IP (`http://<host-ip>:8000`) to access the synchronized library and compiler environment instantly.


---



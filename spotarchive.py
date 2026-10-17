"""SpotArchive: inventory and checksum-verified backup. Does not decrypt or play protected videos."""
import csv
import hashlib
import os
import queue
import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

CHUNK = 1024 * 1024

def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b''):
            digest.update(chunk)
    return digest.hexdigest()

def inventory(root):
    root = Path(root).resolve()
    rows = []
    for directory, _, names in os.walk(root):
        for name in names:
            item = Path(directory) / name
            try:
                relative = item.relative_to(root)
                rows.append(dict(folder=relative.parts[0], path=str(relative),
                                 extension=item.suffix.lower(), size=item.stat().st_size))
            except OSError:
                pass
    return rows

def backup(source, destination, report):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination must be separate folders')
    files = [Path(root) / name for root, _, names in os.walk(source) for name in names]
    for index, original in enumerate(files, 1):
        relative = original.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if original.stat().st_size == target.stat().st_size and sha256(original) == sha256(target):
                report(f'{index}/{len(files)} Already verified: {relative}')
                continue
            raise FileExistsError(f'Destination file differs: {target}')
        temporary = target.with_name(target.name + '.partial-copy')
        try:
            with open(original, 'rb') as inp, open(temporary, 'wb') as out:
                shutil.copyfileobj(inp, out, CHUNK)
            if sha256(original) != sha256(temporary):
                raise IOError(f'Checksum mismatch: {relative}')
            temporary.rename(target)
            report(f'{index}/{len(files)} Verified: {relative}')
        finally:
            if temporary.exists():
                temporary.unlink()
    return len(files)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('SpotArchive - Verified Backup (No Playback)')
        self.geometry('850x575')
        self.source = tk.StringVar()
        self.destination = tk.StringVar()
        self.rows = []
        self.events = queue.Queue()
        main = ttk.Frame(self, padding=15)
        main.pack(fill='both', expand=True)
        ttk.Label(main, text='SpotArchive - inventory and verified backups',
                  font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(main, text='Does not decrypt or play .spot videos. Never deletes originals.').pack(anchor='w', pady=7)
        for label, var in [('Source folder', self.source), ('Backup destination', self.destination)]:
            line = ttk.Frame(main)
            line.pack(fill='x', pady=5)
            ttk.Label(line, text=label, width=21).pack(side='left')
            ttk.Entry(line, textvariable=var).pack(side='left', fill='x', expand=True)
            ttk.Button(line, text='Browse', command=lambda v=var: v.set(filedialog.askdirectory() or v.get())).pack(side='left')
        buttons = ttk.Frame(main)
        buttons.pack(fill='x', pady=9)
        ttk.Button(buttons, text='Scan', command=self.scan).pack(side='left', padx=3)
        ttk.Button(buttons, text='Export CSV', command=self.export).pack(side='left', padx=3)
        ttk.Button(buttons, text='Copy and verify', command=self.copy).pack(side='left', padx=3)
        self.status = ttk.Label(main, text='Choose a source folder.')
        self.status.pack(anchor='w')
        self.tree = ttk.Treeview(main, columns=('folder','all','spot','mib'), show='headings')
        for key, title, width in [('folder','Folder',400),('all','Files',90),('spot','.spot files',100),('mib','MiB',100)]:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width)
        self.tree.pack(fill='both', expand=True, pady=8)
        self.logs = tk.Text(main, height=6, state='disabled')
        self.logs.pack(fill='x')
        self.after(150, self.poll)

    def poll(self):
        while not self.events.empty():
            kind, value = self.events.get()
            if kind == 'log':
                self.logs.config(state='normal')
                self.logs.insert('end', value + '\n')
                self.logs.see('end')
                self.logs.config(state='disabled')
            elif kind == 'error':
                messagebox.showerror('SpotArchive', value)
            else:
                messagebox.showinfo('SpotArchive', value)
        self.after(150, self.poll)

    def scan(self):
        source = Path(self.source.get())
        if not source.is_dir():
            messagebox.showerror('Source', 'Choose an existing folder.')
            return
        self.rows = inventory(source)
        groups = {}
        for row in self.rows:
            group = groups.setdefault(row['folder'], [0, 0, 0])
            group[0] += 1
            group[1] += row['extension'] == '.spot'
            group[2] += row['size']
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)
        for name, counts in sorted(groups.items()):
            self.tree.insert('', 'end', values=(name, counts[0], counts[1], round(counts[2]/1048576, 2)))
        self.status.config(text=f'{len(groups)} groups; {len(self.rows)} files; {sum(r["size"] for r in self.rows)/1073741824:.2f} GiB')

    def export(self):
        if not self.rows:
            messagebox.showwarning('SpotArchive', 'Scan first')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if path:
            with open(path, 'w', encoding='utf-8-sig', newline='') as out:
                writer = csv.DictWriter(out, fieldnames=['folder','path','extension','size'])
                writer.writeheader()
                writer.writerows(self.rows)
            messagebox.showinfo('SpotArchive', 'Saved CSV')

    def copy(self):
        source, dest = Path(self.source.get()), self.destination.get()
        if not source.is_dir() or not dest:
            messagebox.showerror('SpotArchive', 'Choose source and destination folders')
            return
        if not messagebox.askyesno('Confirm', 'Copy files and compare SHA-256? Originals will remain untouched.'):
            return
        def worker():
            try:
                total = backup(source, dest, lambda msg: self.events.put(('log', msg)))
                self.events.put(('done', f'{total} files verified. Keep your originals until playback is confirmed.'))
            except Exception as error:
                self.events.put(('error', str(error)))
        threading.Thread(target=worker, daemon=True).start()

if __name__ == '__main__':
    App().mainloop()

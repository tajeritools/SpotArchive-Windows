using System.Diagnostics;

namespace SpotArchive.Windows;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        ApplicationConfiguration.Initialize();
        Application.Run(new MainForm());
    }
}

internal sealed class MainForm : Form
{
    private readonly Label _path = new()
    {
        AutoEllipsis = true,
        Dock = DockStyle.Top,
        Font = new Font(SystemFonts.MessageBoxFont, FontStyle.Bold),
        Height = 52,
        Padding = new Padding(14, 14, 14, 4),
        Text = "یک فایل .spot انتخاب یا اینجا رها کنید."
    };
    private readonly Label _details = new()
    {
        Dock = DockStyle.Top,
        Height = 48,
        Padding = new Padding(14, 2, 14, 4),
        Text = "فایل‌های .spot رمزگذاری‌شده‌اند و فقط با مجوز ناشر، در SpotPlayer رسمی پخش می‌شوند."
    };
    private readonly Button _open = new() { Text = "باز کردن در SpotPlayer", Enabled = false, AutoSize = true };
    private string? _selectedFile;

    public MainForm()
    {
        Text = "Spot Archive for Windows";
        StartPosition = FormStartPosition.CenterScreen;
        ClientSize = new Size(620, 230);
        MinimumSize = new Size(500, 250);
        AllowDrop = true;
        DragEnter += OnDragEnter;
        DragDrop += OnDragDrop;

        var browse = new Button { Text = "انتخاب فایل .spot", AutoSize = true };
        browse.Click += (_, _) => Browse();
        _open.Click += (_, _) => OpenSelectedFile();

        var buttons = new FlowLayoutPanel
        {
            Dock = DockStyle.Bottom,
            FlowDirection = FlowDirection.RightToLeft,
            Height = 64,
            Padding = new Padding(14),
            WrapContents = false
        };
        buttons.Controls.Add(_open);
        buttons.Controls.Add(browse);

        var help = new LinkLabel
        {
            AutoSize = true,
            Dock = DockStyle.Bottom,
            Padding = new Padding(14, 4, 14, 14),
            Text = "راهنما: اگر SpotPlayer نصب نیست، فایل با دوبارکلیک نیز قابل پخش نیست."
        };
        help.LinkClicked += (_, _) => ShowHelp();

        Controls.Add(help);
        Controls.Add(buttons);
        Controls.Add(_details);
        Controls.Add(_path);
    }

    private void Browse()
    {
        using var dialog = new OpenFileDialog
        {
            Filter = "SpotPlayer files (*.spot)|*.spot|All files (*.*)|*.*",
            Title = "انتخاب فایل SpotPlayer"
        };
        if (dialog.ShowDialog(this) == DialogResult.OK) SelectFile(dialog.FileName);
    }

    private void OnDragEnter(object? sender, DragEventArgs e)
    {
        e.Effect = e.Data?.GetDataPresent(DataFormats.FileDrop) == true
            ? DragDropEffects.Copy : DragDropEffects.None;
    }

    private void OnDragDrop(object? sender, DragEventArgs e)
    {
        if (e.Data?.GetData(DataFormats.FileDrop) is not string[] files || files.Length != 1) return;
        SelectFile(files[0]);
    }

    private void SelectFile(string path)
    {
        if (!File.Exists(path)) return;
        if (!string.Equals(Path.GetExtension(path), ".spot", StringComparison.OrdinalIgnoreCase))
        {
            MessageBox.Show(this, "فایل انتخاب‌شده پسوند .spot ندارد.", Text, MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        var info = new FileInfo(path);
        _selectedFile = path;
        _path.Text = path;
        _details.Text = $"{info.Length / 1024d / 1024d:N1} MB  •  آخرین تغییر: {info.LastWriteTime:G}";
        _open.Enabled = true;
    }

    private void OpenSelectedFile()
    {
        if (_selectedFile is null) return;

        try
        {
            Process.Start(new ProcessStartInfo(_selectedFile) { UseShellExecute = true });
        }
        catch (Exception exception)
        {
            MessageBox.Show(this,
                "ویندوز هیچ برنامه‌ای برای باز کردن .spot پیدا نکرد. SpotPlayer رسمی را نصب کرده و با مجوز ناشر وارد شوید.\n\n" +
                exception.Message,
                Text, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void ShowHelp()
    {
        MessageBox.Show(this,
            "این ابزار رمزگذاری یا مجوز .spot را دور نمی‌زند.\n\n" +
            "برای پخش، SpotPlayer رسمی را نصب کنید و با حساب/کد مجاز ناشر دوره وارد شوید. سپس این فایل را دوباره باز کنید.",
            "راهنمای پخش فایل .spot", MessageBoxButtons.OK, MessageBoxIcon.Information);
    }
}

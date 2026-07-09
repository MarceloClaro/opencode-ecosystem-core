Add-Type -AssemblyName System.Drawing

$inputPath = "C:\Users\marce\.gemini\antigravity-cli\brain\255293ea-a76a-49ae-9ced-20c7fcf8659c\holographic_tooth_1781947196117.jpg"
$outputPath = "C:\Users\marce\Documents\OpenCode_Ecosystem\livro_gemeos_odontologia\images\capa_logo_transparent.png"

$bmp = [System.Drawing.Bitmap]::FromFile($inputPath)
$newBmp = New-Object System.Drawing.Bitmap($bmp.Width, $bmp.Height)

for ($y = 0; $y -lt $bmp.Height; $y++) {
    for ($x = 0; $x -lt $bmp.Width; $x++) {
        $pixel = $bmp.GetPixel($x, $y)
        $lum = 0.299 * $pixel.R + 0.587 * $pixel.G + 0.114 * $pixel.B
        if ($lum -lt 30) {
            $newBmp.SetPixel($x, $y, [System.Drawing.Color]::Transparent)
        } else {
            # smooth alpha
            $alpha = [math]::Min(255, [math]::Max(0, [int](($lum - 30) * 5)))
            $newColor = [System.Drawing.Color]::FromArgb($alpha, $pixel.R, $pixel.G, $pixel.B)
            $newBmp.SetPixel($x, $y, $newColor)
        }
    }
}

$newBmp.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
$newBmp.Dispose()
Write-Host "Conversao concluida!"

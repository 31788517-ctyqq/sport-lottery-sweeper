# PowerShell测试脚本
$body = @{
    email = "admin@example.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/login' -Method Post -ContentType 'application/json' -Body $body
    Write-Host "✅ 登录成功!" -ForegroundColor Green
    Write-Host "响应数据:" $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ 登录失败:" $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $responseStream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($responseStream)
        $responseBody = $reader.ReadToEnd()
        Write-Host "错误详情:" $responseBody -ForegroundColor Red
    }
}
param(
  [Parameter(Mandatory=$true)]
  [ValidateSet('list-windows','snapshot','invoke','set-value','focus','read','focused','set-focused','invoke-focused')]
  [string]$Command,
  [string]$Window = '',
  [string]$Name = '',
  [string]$Value = '',
  [int]$MaxDepth = 6
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement

function Out-Json($payload) {
  $payload | ConvertTo-Json -Depth 12 -Compress
}

function Get-Windows {
  $root.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition) |
    Where-Object { $_.Current.Name } |
    ForEach-Object {
      [ordered]@{
        name = $_.Current.Name
        class = $_.Current.ClassName
        pid = $_.Current.ProcessId
        type = $_.Current.ControlType.ProgrammaticName
        enabled = $_.Current.IsEnabled
        rect = $_.Current.BoundingRectangle.ToString()
      }
    }
}

function Find-Window([string]$title) {
  $matches = @(Get-Windows | Where-Object {
    $_.name.IndexOf($title, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
  })
  if ($matches.Count -eq 0) { throw 'WINDOW_NOT_FOUND' }
  if ($matches.Count -gt 1) { throw 'AMBIGUOUS_WINDOW' }
  $all = $root.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)
  foreach ($element in $all) {
    if ($element.Current.Name -eq $matches[0].name) { return $element }
  }
  throw 'WINDOW_NOT_FOUND'
}

function Get-Patterns($element) {
  $found = @()
  foreach ($pair in @(
      @('invoke', [System.Windows.Automation.InvokePattern]::Pattern),
      @('value', [System.Windows.Automation.ValuePattern]::Pattern),
      @('selection', [System.Windows.Automation.SelectionItemPattern]::Pattern),
      @('expand', [System.Windows.Automation.ExpandCollapsePattern]::Pattern),
      @('text', [System.Windows.Automation.TextPattern]::Pattern))) {
    $pattern = $null
    try {
      if ($element.TryGetCurrentPattern($pair[1], [ref]$pattern)) { $found += $pair[0] }
    } catch { }
  }
  $found
}

function Walk($element, [int]$depth) {
  if ($null -eq $element) { return $null }
  $node = [ordered]@{
    name = $element.Current.Name
    type = $element.Current.ControlType.ProgrammaticName
    automation_id = $element.Current.AutomationId
    enabled = $element.Current.IsEnabled
    patterns = @(Get-Patterns $element)
  }
  if ($depth -lt $MaxDepth) {
    $children = New-Object System.Collections.ArrayList
    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $child = $walker.GetFirstChild($element)
    $count = 0
    while ($null -ne $child -and $count -lt 200) {
      $serialized = Walk $child ($depth + 1)
      if ($null -ne $serialized) { [void]$children.Add($serialized) }
      $child = $walker.GetNextSibling($child)
      $count++
    }
    if ($children.Count -gt 0) { $node.children = @($children) }
  }
  $node
}

function Get-TopWindow($element) {
  $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
  $current = $element
  while ($null -ne $current) {
    $parent = $walker.GetParent($current)
    if ($null -eq $parent -or $parent -eq $root) { return $current }
    $current = $parent
  }
  return $element
}

function Find-Element($window, [string]$label) {
  $condition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::NameProperty, $label)
  $exact = @($window.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition))
  if ($exact.Count -eq 1) { return $exact[0] }
  if ($exact.Count -gt 1) {
    $actionable = @($exact | Where-Object {
        $patterns = @(Get-Patterns $_)
        $patterns -contains 'invoke' -or $patterns -contains 'selection' -or $patterns -contains 'expand'
      })
    if ($actionable.Count -eq 1) { return $actionable[0] }
    throw 'AMBIGUOUS_ELEMENT'
  }
  $all = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition)
  $contains = @($all | Where-Object {
    $_.Current.Name -and $_.Current.Name.IndexOf($label, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
  })
  if ($contains.Count -eq 0) { throw 'ELEMENT_NOT_FOUND' }
  if ($contains.Count -gt 1) { throw 'AMBIGUOUS_ELEMENT' }
  return $contains[0]
}

try {
  switch ($Command) {
    'list-windows' {
      Out-Json ([ordered]@{ ok = $true; command = $Command; data = @(Get-Windows) })
    }
    'snapshot' {
      $win = Find-Window $Window
      Out-Json ([ordered]@{ ok = $true; command = $Command; data = (Walk $win 0) })
    }
    'read' {
      $win = Find-Window $Window
      $texts = @()
      $all = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition)
      foreach ($element in $all) {
        if ($element.Current.Name) {
          $texts += [ordered]@{
            name = $element.Current.Name
            type = $element.Current.ControlType.ProgrammaticName
            enabled = $element.Current.IsEnabled
          }
        }
      }
      Out-Json ([ordered]@{ ok = $true; command = $Command; data = @($texts) })
    }
    'invoke' {
      $win = Find-Window $Window
      $element = Find-Element $win $Name
      $pattern = $null
      if ($element.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$pattern)) {
        $pattern.Invoke()
        Out-Json ([ordered]@{ ok = $true; command = $Command; data = [ordered]@{ method = 'invoke'; name = $Name } })
      } elseif ($element.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$pattern)) {
        $pattern.Select()
        Out-Json ([ordered]@{ ok = $true; command = $Command; data = [ordered]@{ method = 'select'; name = $Name } })
      } elseif ($element.TryGetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern, [ref]$pattern)) {
        $pattern.Expand()
        Out-Json ([ordered]@{ ok = $true; command = $Command; data = [ordered]@{ method = 'expand'; name = $Name } })
      } else {
        throw 'NO_ACTION'
      }
    }
    'set-value' {
      $win = Find-Window $Window
      $element = Find-Element $win $Name
      $pattern = $null
      if (-not $element.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$pattern)) {
        throw 'NO_VALUE_PATTERN'
      }
      $pattern.SetValue($Value)
      Out-Json ([ordered]@{ ok = $true; command = $Command; data = [ordered]@{ name = $Name; chars = $Value.Length } })
    }
    'focus' {
      $win = Find-Window $Window
      $win.SetFocus()
      Out-Json ([ordered]@{ ok = $true; command = $Command; data = [ordered]@{ name = $win.Current.Name } })
    }
    'focused' {
      $element = [System.Windows.Automation.AutomationElement]::FocusedElement
      if ($null -eq $element) { throw 'NO_FOCUS' }
      $top = Get-TopWindow $element
      Out-Json ([ordered]@{ ok = $true; command = $Command; data = [ordered]@{
            name = $element.Current.Name
            type = $element.Current.ControlType.ProgrammaticName
            automation_id = $element.Current.AutomationId
            patterns = @(Get-Patterns $element)
            window = $top.Current.Name
          } })
    }
    'set-focused' {
      $element = [System.Windows.Automation.AutomationElement]::FocusedElement
      if ($null -eq $element) { throw 'NO_FOCUS' }
      $top = Get-TopWindow $element
      $pattern = $null
      if (-not $element.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$pattern)) {
        throw 'NO_VALUE_PATTERN'
      }
      $pattern.SetValue($Value)
      Out-Json ([ordered]@{ ok = $true; command = $Command; data = [ordered]@{
            window = $top.Current.Name; chars = $Value.Length
          } })
    }
    'invoke-focused' {
      $element = [System.Windows.Automation.AutomationElement]::FocusedElement
      if ($null -eq $element) { throw 'NO_FOCUS' }
      $top = Get-TopWindow $element
      $pattern = $null
      if ($element.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$pattern)) {
        $pattern.Invoke()
      } elseif ($element.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$pattern)) {
        $pattern.Select()
      } else { throw 'NO_ACTION' }
      Out-Json ([ordered]@{ ok = $true; command = $Command; data = [ordered]@{ window = $top.Current.Name } })
    }
  }
} catch {
  Out-Json ([ordered]@{
      ok = $false
      command = $Command
      error = [ordered]@{ code = $_.Exception.Message; message = $_.Exception.Message }
    })
  exit 1
}

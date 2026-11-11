--!strict
-- Spins the part this script is parented to. Speed is in degrees per second.

local RunService = game:GetService("RunService")

local part = script.Parent :: BasePart
local degreesPerSecond = 90

RunService.Heartbeat:Connect(function(deltaTime: number)
	part.CFrame *= CFrame.Angles(0, math.rad(degreesPerSecond * deltaTime), 0)
end)

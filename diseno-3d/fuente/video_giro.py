"""
video_giro.py — Video de giro (turntable) del gemelo 3D completo.

Genera ../renders/SCB_gemelo_completo_giro.mp4: 12 s a 30 fps, 1516 × 1152, una vuelta
completa que se repite sin salto (para la presentación).
Uso:  python video_giro.py video        (o "previa" para 8 cuadros de prueba en PNG)
Requiere cadquery, vtk y ffmpeg en el PATH. Antes corran gemelo_completo.py.
"""
import math, os, subprocess, sys, tempfile
import cadquery as cq, vtk

AQUI = os.path.dirname(os.path.abspath(__file__))
STEP = os.path.join(AQUI, "..", "SCB_gemelo_completo.step")
SALIDA = os.path.join(AQUI, "..", "renders")
W, H, FPS, SEG = 1516, 1152, 30, 12
FONDO = (0x0b / 255, 0x10 / 255, 0x20 / 255)
EL = math.radians(28)
AZ0 = math.radians(-61)
modo = sys.argv[1] if len(sys.argv) > 1 else "video"   # "previa" o "video"
DIST = float(sys.argv[2]) if len(sys.argv) > 2 else 1190
FOCO = (0.0, 50.0, 0.0)

TMP = tempfile.mkdtemp()
asm = cq.Assembly.importStep(STEP)
rw = vtk.vtkRenderWindow(); rw.SetOffScreenRendering(1); rw.SetSize(W, H); rw.SetMultiSamples(0)
r = vtk.vtkRenderer(); r.SetBackground(*FONDO); r.SetUseFXAA(True); rw.AddRenderer(r)
lo = [1e9] * 3; hi = [-1e9] * 3
for i, (shape, nombre, loc, color) in enumerate(asm):
    if shape is None: continue
    s = shape.moved(loc); b = s.BoundingBox()
    lo = [min(a, v) for a, v in zip(lo, (b.xmin, b.ymin, b.zmin))]; hi = [max(a, v) for a, v in zip(hi, (b.xmax, b.ymax, b.zmax))]
    ruta = os.path.join(TMP, f"{i}.stl"); cq.exporters.export(s, ruta, tolerance=0.12, angularTolerance=0.3)
    rd = vtk.vtkSTLReader(); rd.SetFileName(ruta); rd.Update(); pd = rd.GetOutput()
    rgb = color.toTuple()[:3] if color else (0.75, 0.75, 0.75)
    nm = vtk.vtkPolyDataNormals(); nm.SetInputData(pd); nm.SetFeatureAngle(35); nm.SplittingOn()
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(nm.GetOutputPort())
    a = vtk.vtkActor(); a.SetMapper(m); p = a.GetProperty(); p.SetColor(*rgb)
    p.SetAmbient(0.25); p.SetDiffuse(0.78); p.SetSpecular(0.2); p.SetSpecularPower(25); r.AddActor(a)
    fe = vtk.vtkFeatureEdges(); fe.SetInputData(pd); fe.BoundaryEdgesOn(); fe.FeatureEdgesOn(); fe.SetFeatureAngle(40)
    fe.ManifoldEdgesOff(); fe.NonManifoldEdgesOff(); fe.ColoringOff()
    me = vtk.vtkPolyDataMapper(); me.SetInputConnection(fe.GetOutputPort()); me.SetResolveCoincidentTopologyToPolygonOffset()
    ae = vtk.vtkActor(); ae.SetMapper(me); ae.GetProperty().SetColor(0.1, 0.1, 0.1); ae.GetProperty().SetLineWidth(1.3); r.AddActor(ae)
print("bbox", [round(v) for v in lo], [round(v) for v in hi], flush=True)
lk = vtk.vtkLightKit(); lk.SetKeyLightIntensity(0.95); lk.AddLightsToRenderer(r)
cam = r.GetActiveCamera(); cam.SetViewAngle(28); cam.SetViewUp(0, 0, 1)
w2i = vtk.vtkWindowToImageFilter(); w2i.SetInput(rw); w2i.SetInputBufferTypeToRGB(); w2i.ReadFrontBufferOff()

def cuadro(az):
    cam.SetFocalPoint(*FOCO)
    cam.SetPosition(FOCO[0] + DIST * math.cos(EL) * math.cos(az), FOCO[1] + DIST * math.cos(EL) * math.sin(az), FOCO[2] + DIST * math.sin(EL))
    cam.SetViewUp(0, 0, 1); r.ResetCameraClippingRange(); rw.Render(); w2i.Modified(); w2i.Update()
    return w2i.GetOutput()

if modo == "previa":
    for k, grados in enumerate((0, 45, 90, 135, 180, 225, 270, 315)):
        img = cuadro(AZ0 + math.radians(grados))
        wr = vtk.vtkPNGWriter(); wr.SetFileName(os.path.join(SALIDA, f"previa_{k}.png")); wr.SetInputData(img); wr.Write()
    print("previas listas")
else:
    from vtk.util.numpy_support import vtk_to_numpy
    n = FPS * SEG
    tmp = os.path.join(SALIDA, "giro_tmp.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-vf", "vflip", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp],
                          stdin=subprocess.PIPE)
    for f in range(n):
        img = cuadro(AZ0 + 2 * math.pi * f / n)   # giro completo y sin salto al repetirse
        ff.stdin.write(vtk_to_numpy(img.GetPointData().GetScalars()).tobytes())
        if f % 60 == 0: print("cuadro", f, "/", n, flush=True)
    ff.stdin.close()
    if ff.wait() == 0:
        os.replace(tmp, os.path.join(SALIDA, "SCB_gemelo_completo_giro.mp4")); print("video listo")
